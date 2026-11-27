"""Upload tests. Run: python manage.py test uploads

Every test writes into a throw-away temporary folder, never into your real media/ folder.
"""
import io
import re
import shutil
import tempfile
from pathlib import Path

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.management import call_command
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from PIL import Image

from .models import PortalDocument, StudentDocument, StudentPhoto
from .utils import clean_display_name

User = get_user_model()
MB = 1024 * 1024
PDF_BYTES = b"%PDF-1.4\n1 0 obj\n<< /Type /Catalog >>\nendobj\ntrailer\n<< /Root 1 0 R >>\n%%EOF\n"
UUID_NAME = re.compile(r"^[0-9a-f]{32}\.[a-z]+$")


def png_bytes(width=10, height=10, fmt="PNG"):
    buffer = io.BytesIO()
    Image.new("RGB", (width, height), "red").save(buffer, fmt)
    return buffer.getvalue()


class TempStorageTestCase(TestCase):
    """Point MEDIA_ROOT, PRIVATE_MEDIA_ROOT and STATIC_ROOT at temporary folders."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        override = override_settings(
            MEDIA_ROOT=self.tmp / "media",
            PRIVATE_MEDIA_ROOT=self.tmp / "private",
            STATIC_ROOT=self.tmp / "static",
        )
        override.enable()
        self.addCleanup(override.disable)

    def stored_files(self, root):
        base = self.tmp / root
        return [p for p in base.rglob("*") if p.is_file()] if base.exists() else []


# ======================================================================= normal Django form
class UploadViewTests(TempStorageTestCase):
    def post(self, name="notes.pdf", content=b"fake pdf content", student="Aarav Sharma", **extra):
        uploaded = SimpleUploadedFile(name, content, content_type="application/pdf")
        return self.client.post(reverse("uploads:upload"), {"student_name": student, "document": uploaded}, **extra)

    def test_get_shows_multipart_form_with_csrf_token(self):
        response = self.client.get(reverse("uploads:upload"))
        self.assertContains(response, 'enctype="multipart/form-data"')
        self.assertContains(response, "csrfmiddlewaretoken")

    def test_valid_document_upload(self):                          # slide test
        response = self.post()
        self.assertEqual(response.status_code, 302)
        self.assertEqual(StudentDocument.objects.count(), 1)

    def test_rejects_large_document(self):                         # slide test
        response = self.post("large.pdf", b"x" * (5 * MB + 1))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "smaller than 5 MB")
        self.assertEqual(StudentDocument.objects.count(), 0)
        self.assertEqual(self.stored_files("media"), [])           # nothing was written to disk

    def test_exactly_five_mb_is_accepted(self):
        self.assertEqual(self.post("edge.pdf", b"x" * (5 * MB)).status_code, 302)

    def test_rejects_wrong_extension(self):
        response = self.post("virus.exe", b"MZ")
        self.assertContains(response, "Only PDF, TXT, and DOCX files are allowed.")
        self.assertEqual(StudentDocument.objects.count(), 0)

    def test_rejects_double_extension(self):
        self.assertContains(self.post("report.pdf.exe"), "Only PDF, TXT, and DOCX")

    def test_rejects_file_without_extension(self):
        self.assertContains(self.post("README"), "Only PDF, TXT, and DOCX")

    def test_uppercase_extension_is_accepted(self):
        self.assertEqual(self.post("NOTES.PDF").status_code, 302)

    def test_all_three_allowed_types(self):
        for name in ("a.pdf", "b.txt", "c.docx"):
            self.assertEqual(self.post(name).status_code, 302, name)

    def test_missing_file_is_an_error(self):
        response = self.client.post(reverse("uploads:upload"), {"student_name": "Aarav"})
        self.assertContains(response, "This field is required")

    def test_missing_enctype_means_no_file(self):
        # a browser form WITHOUT enctype="multipart/form-data" sends only the file NAME as text,
        # so request.FILES is empty and the form says the file is missing
        response = self.client.post(reverse("uploads:upload"), {"student_name": "Aarav", "document": "notes.pdf"})
        self.assertContains(response, "This field is required")
        self.assertEqual(StudentDocument.objects.count(), 0)

    def test_stored_name_is_generated_not_user_supplied(self):
        self.post("my secret résumé.pdf")
        stored = Path(StudentDocument.objects.get().document.name)
        self.assertRegex(stored.name, UUID_NAME)
        self.assertNotIn("secret", stored.name)
        self.assertEqual(stored.suffix, ".pdf")                    # extension preserved

    def test_path_traversal_name_cannot_escape_the_media_folder(self):
        self.post("../../evil.pdf")
        document = StudentDocument.objects.get()
        path = Path(document.document.path).resolve()
        self.assertTrue(str(path).startswith(str((self.tmp / "media").resolve())))
        self.assertRegex(path.name, UUID_NAME)

    def test_two_uploads_with_the_same_name_do_not_collide(self):
        self.post("same.pdf")
        self.post("same.pdf")
        names = {d.document.name for d in StudentDocument.objects.all()}
        self.assertEqual(len(names), 2)
        self.assertEqual(len(self.stored_files("media")), 2)

    def test_file_is_stored_in_dated_subfolder(self):
        self.post()
        self.assertRegex(StudentDocument.objects.get().document.name, r"^student_documents/\d{4}/\d{2}/")

    def test_file_content_is_saved_intact(self):
        self.post(content=b"hello world")
        with StudentDocument.objects.get().document.open("rb") as f:
            self.assertEqual(f.read(), b"hello world")

    def test_post_without_csrf_token_is_forbidden(self):
        strict = Client(enforce_csrf_checks=True)
        uploaded = SimpleUploadedFile("a.pdf", b"x")
        response = strict.post(reverse("uploads:upload"), {"student_name": "A", "document": uploaded})
        self.assertEqual(response.status_code, 403)

    def test_upload_is_logged(self):
        with self.assertLogs("uploads.views", level="INFO") as logs:
            self.post()
        self.assertTrue(any("Document uploaded: id=" in line for line in logs.output))


# ======================================================================= images
class PhotoUploadTests(TempStorageTestCase):
    def post(self, name="me.png", content=None):
        content = png_bytes() if content is None else content
        return self.client.post(reverse("uploads:upload-photo"),
                                {"photo": SimpleUploadedFile(name, content, content_type="image/png")})

    def test_valid_png(self):
        self.assertEqual(self.post().status_code, 302)
        self.assertRegex(Path(StudentPhoto.objects.get().photo.name).name, UUID_NAME)

    def test_valid_jpeg(self):
        self.assertEqual(self.post("me.jpg", png_bytes(fmt="JPEG")).status_code, 302)

    def test_text_renamed_to_png_is_rejected(self):
        # extension alone proves nothing: Pillow must be able to decode the content
        response = self.post("fake.png", b"this is not an image")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "valid image")
        self.assertEqual(StudentPhoto.objects.count(), 0)

    def test_gif_extension_rejected(self):
        response = self.post("anim.gif", png_bytes(fmt="GIF"))
        self.assertContains(response, "File extension")

    def test_too_many_pixels_rejected(self):
        response = self.post("wide.png", png_bytes(4001, 1))
        self.assertContains(response, "must not exceed 4000 by 4000 pixels")

    def test_exact_dimension_limit_accepted(self):
        self.assertEqual(self.post("limit.png", png_bytes(4000, 1)).status_code, 302)

    def test_file_over_two_mb_rejected(self):
        big = png_bytes() + b"\0" * (2 * MB)            # still a decodable PNG, but too large
        self.assertContains(self.post("big.png", big), "smaller than 2 MB")


# ======================================================================= REST API (lecture)
class DocumentAPITests(TempStorageTestCase):
    url = property(lambda self: reverse("uploads:document-api"))

    def post(self, name="sample.pdf", content=b"%PDF- data", **data):
        payload = {"student_name": "Aarav Sharma", "document": SimpleUploadedFile(name, content)}
        payload.update(data)
        return self.client.post(self.url, payload)           # multipart by default

    def test_valid_upload_returns_201_with_json(self):
        response = self.post()
        self.assertEqual(response.status_code, 201)
        body = response.json()
        self.assertEqual(body["student_name"], "Aarav Sharma")
        self.assertRegex(body["document"], r"/media/student_documents/\d{4}/\d{2}/[0-9a-f]{32}\.pdf$")
        self.assertIn("id", body)
        self.assertEqual(StudentDocument.objects.count(), 1)

    def test_large_file_returns_400_with_message(self):
        response = self.post("big.pdf", b"x" * (5 * MB + 1))
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {"document": ["The file must be smaller than 5 MB."]})

    def test_bad_extension_returns_400(self):
        response = self.post("run.sh", b"#!/bin/sh")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["document"], ["Only PDF, TXT, and DOCX files are allowed."])

    def test_missing_fields(self):
        response = self.client.post(self.url, {})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(set(response.json()), {"student_name", "document"})

    def test_client_cannot_set_id_or_date(self):
        response = self.post(id=999, uploaded_at="2000-01-01T00:00:00Z")
        self.assertNotEqual(response.json()["id"], 999)
        self.assertNotIn("2000-01-01", response.json()["uploaded_at"])

    def test_json_body_is_not_accepted_for_files(self):
        response = self.client.post(self.url, {"student_name": "A"}, content_type="application/json")
        self.assertEqual(response.status_code, 415)           # only multipart / form parsers


# ======================================================================= private portal (PBL)
def make_user(name="alice"):
    return User.objects.create_user(name, password="pw-12345-x")


def pdf(name="assignment.pdf", content=PDF_BYTES):
    return SimpleUploadedFile(name, content, content_type="application/pdf")


class PortalTestCase(TempStorageTestCase):
    def setUp(self):
        super().setUp()
        self.alice = make_user("alice")
        self.bob = make_user("bob")

    def upload_as(self, user, file=None):
        client = Client()
        client.force_login(user)
        return client, client.post(reverse("uploads:portal"), {"file": file or pdf()})


class PortalUploadTests(PortalTestCase):
    def test_valid_pdf_upload(self):
        _, response = self.upload_as(self.alice)
        self.assertRedirects(response, reverse("uploads:portal"))
        doc = PortalDocument.objects.get()
        self.assertEqual(doc.owner, self.alice)
        self.assertEqual(doc.original_name, "assignment.pdf")
        self.assertEqual(doc.size, len(PDF_BYTES))

    def test_stored_name_is_uuid_and_original_name_kept_separately(self):
        self.upload_as(self.alice, pdf("My Assignment (final).pdf"))
        doc = PortalDocument.objects.get()
        self.assertRegex(Path(doc.file.name).name, UUID_NAME)
        self.assertEqual(Path(doc.file.name).suffix, ".pdf")
        self.assertEqual(doc.original_name, "My Assignment (final).pdf")

    def test_uppercase_pdf_extension_is_stored_as_lowercase_pdf(self):
        self.upload_as(self.alice, pdf("SCAN.PDF"))
        self.assertTrue(PortalDocument.objects.get().file.name.endswith(".pdf"))

    def test_anonymous_is_redirected_to_login(self):
        response = self.client.post(reverse("uploads:portal"), {"file": pdf()})
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith("/accounts/login/"))
        self.assertEqual(PortalDocument.objects.count(), 0)

    def test_non_pdf_extension_rejected(self):
        _, response = self.upload_as(self.alice, SimpleUploadedFile("notes.txt", PDF_BYTES))
        self.assertContains(response, "Only PDF files are allowed.")
        self.assertEqual(PortalDocument.objects.count(), 0)

    def test_docx_rejected_even_though_the_other_endpoint_accepts_it(self):
        _, response = self.upload_as(self.alice, SimpleUploadedFile("essay.docx", b"PK\x03\x04"))
        self.assertContains(response, "Only PDF files are allowed.")

    def test_renamed_non_pdf_content_rejected(self):
        # a text file / exe renamed to .pdf: the content check catches it
        for payload in (b"just text", b"MZ\x90\x00 exe", b""):
            _, response = self.upload_as(self.alice, pdf("evil.pdf", payload))
            self.assertEqual(response.status_code, 200)
            self.assertTrue("not a valid PDF" in response.content.decode() or "empty" in response.content.decode())
        self.assertEqual(PortalDocument.objects.count(), 0)

    def test_oversized_pdf_rejected_and_nothing_stored(self):
        _, response = self.upload_as(self.alice, pdf("big.pdf", PDF_BYTES + b"x" * (10 * MB)))
        self.assertContains(response, "at most 10 MB")
        self.assertEqual(PortalDocument.objects.count(), 0)
        self.assertEqual(self.stored_files("private"), [])

    def test_exactly_ten_mb_accepted(self):
        content = PDF_BYTES + b"x" * (10 * MB - len(PDF_BYTES))
        self.assertEqual(len(content), 10 * MB)
        _, response = self.upload_as(self.alice, pdf("edge.pdf", content))
        self.assertEqual(response.status_code, 302)

    def test_hostile_original_name_is_neutralised(self):
        self.upload_as(self.alice, pdf("../../etc/passwd.pdf"))
        self.assertEqual(PortalDocument.objects.get().original_name, "passwd.pdf")

    def test_script_in_file_name_is_escaped_in_the_page(self):
        # (a "/" in the name would be treated as a folder separator and dropped, so none is used)
        client, _ = self.upload_as(self.alice, pdf("<img src=x onerror=alert(1)>.pdf"))
        page = client.get(reverse("uploads:portal"))
        self.assertNotContains(page, "<img src=x")
        self.assertContains(page, "&lt;img src=x onerror=alert(1)&gt;.pdf")

    def test_stored_file_is_outside_the_public_media_folder(self):
        self.upload_as(self.alice)
        stored = Path(PortalDocument.objects.get().file.path).resolve()
        self.assertTrue(str(stored).startswith(str((self.tmp / "private").resolve())))
        self.assertEqual(self.stored_files("media"), [])

    def test_private_file_has_no_public_url(self):
        self.upload_as(self.alice)
        with self.assertRaises(ValueError):
            PortalDocument.objects.get().file.url

    def test_clean_display_name_helper(self):
        self.assertEqual(clean_display_name("C:\\Users\\me\\hw.pdf"), "hw.pdf")
        self.assertEqual(clean_display_name("a\x00b.pdf"), "ab.pdf")
        self.assertEqual(clean_display_name(""), "document.pdf")
        self.assertEqual(len(clean_display_name("a" * 400 + ".pdf")), 255)


class PortalAccessTests(PortalTestCase):
    def setUp(self):
        super().setUp()
        self.alice_client, _ = self.upload_as(self.alice, pdf("alice-homework.pdf"))
        self.bob_client, _ = self.upload_as(self.bob, pdf("bob-homework.pdf", PDF_BYTES + b"bob"))
        self.alice_doc = PortalDocument.objects.get(owner=self.alice)
        self.bob_doc = PortalDocument.objects.get(owner=self.bob)

    def test_list_shows_only_my_files(self):
        page = self.alice_client.get(reverse("uploads:portal"))
        self.assertContains(page, "alice-homework.pdf")
        self.assertNotContains(page, "bob-homework.pdf")

    def test_owner_can_download_with_original_name(self):
        response = self.alice_client.get(reverse("uploads:portal-download", args=[self.alice_doc.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(b"".join(response.streaming_content), PDF_BYTES)
        self.assertIn('attachment; filename="alice-homework.pdf"', response["Content-Disposition"])
        self.assertEqual(response["Content-Type"], "application/pdf")
        self.assertEqual(response["X-Content-Type-Options"], "nosniff")

    def test_other_user_cannot_download_my_file(self):
        response = self.bob_client.get(reverse("uploads:portal-download", args=[self.alice_doc.pk]))
        self.assertEqual(response.status_code, 404)           # 404, not 403: does not confirm the id exists

    def test_other_users_response_is_the_same_as_for_a_missing_id(self):
        other = self.bob_client.get(reverse("uploads:portal-download", args=[self.alice_doc.pk]))
        missing = self.bob_client.get(reverse("uploads:portal-download", args=[99999]))
        self.assertEqual(other.status_code, missing.status_code)

    def test_anonymous_cannot_download(self):
        response = self.client.get(reverse("uploads:portal-download", args=[self.alice_doc.pk]))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith("/accounts/login/"))

    def test_staff_flag_alone_does_not_bypass_ownership(self):
        self.bob.is_staff = True
        self.bob.save()
        response = self.bob_client.get(reverse("uploads:portal-download", args=[self.alice_doc.pk]))
        self.assertEqual(response.status_code, 404)

    def test_private_file_cannot_be_fetched_through_media_url(self):
        name = self.alice_doc.file.name
        self.assertEqual(self.client.get(f"/media/{name}").status_code, 404)

    def test_missing_file_on_disk_gives_404_not_500(self):
        Path(self.alice_doc.file.path).unlink()
        response = self.alice_client.get(reverse("uploads:portal-download", args=[self.alice_doc.pk]))
        self.assertEqual(response.status_code, 404)

    def test_deleting_user_removes_their_records(self):
        self.bob.delete()
        self.assertEqual(PortalDocument.objects.count(), 1)


class PortalAPITests(PortalTestCase):
    list_url = property(lambda self: reverse("uploads:portal-api"))

    def api_client(self, user):
        client = Client()
        client.force_login(user)
        return client

    def test_upload_returns_201_and_download_url(self):
        response = self.api_client(self.alice).post(self.list_url, {"file": pdf()})
        self.assertEqual(response.status_code, 201)
        body = response.json()
        self.assertEqual(body["original_name"], "assignment.pdf")
        self.assertEqual(body["size"], len(PDF_BYTES))
        self.assertTrue(body["download_url"].endswith(f"/uploads/api/portal/{body['id']}/download/"))
        self.assertNotIn("file", body)                          # no path to the stored file is exposed
        self.assertNotIn("private", str(body))
        self.assertEqual(PortalDocument.objects.get().owner, self.alice)

    def test_anonymous_cannot_upload_or_list(self):
        self.assertEqual(self.client.post(self.list_url, {"file": pdf()}).status_code, 403)
        self.assertEqual(self.client.get(self.list_url).status_code, 403)
        self.assertEqual(PortalDocument.objects.count(), 0)

    def test_basic_auth_works_for_curl(self):
        import base64
        token = base64.b64encode(b"alice:pw-12345-x").decode()
        response = Client().post(self.list_url, {"file": pdf()}, HTTP_AUTHORIZATION=f"Basic {token}")
        self.assertEqual(response.status_code, 201)

    def test_wrong_basic_auth_password_rejected(self):
        import base64
        token = base64.b64encode(b"alice:wrong").decode()
        response = Client().get(self.list_url, HTTP_AUTHORIZATION=f"Basic {token}")
        self.assertIn(response.status_code, (401, 403))

    def test_invalid_extension_400(self):
        response = self.api_client(self.alice).post(self.list_url, {"file": SimpleUploadedFile("a.txt", PDF_BYTES)})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {"file": ["Only PDF files are allowed."]})

    def test_fake_pdf_400(self):
        response = self.api_client(self.alice).post(self.list_url, {"file": pdf("fake.pdf", b"not a pdf")})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {"file": ["This file is not a valid PDF."]})

    def test_oversized_400(self):
        big = pdf("big.pdf", PDF_BYTES + b"x" * (10 * MB))
        response = self.api_client(self.alice).post(self.list_url, {"file": big})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {"file": ["The file must be at most 10 MB."]})

    def test_missing_file_400(self):
        response = self.api_client(self.alice).post(self.list_url, {})
        self.assertEqual(response.status_code, 400)
        self.assertIn("file", response.json())

    def test_cannot_choose_the_owner(self):
        response = self.api_client(self.alice).post(self.list_url, {"file": pdf(), "owner": self.bob.pk})
        self.assertEqual(response.status_code, 201)
        self.assertEqual(PortalDocument.objects.get().owner, self.alice)

    def test_list_returns_only_my_documents(self):
        alice, bob = self.api_client(self.alice), self.api_client(self.bob)
        alice.post(self.list_url, {"file": pdf("a.pdf")})
        bob.post(self.list_url, {"file": pdf("b.pdf")})
        names = [d["original_name"] for d in alice.get(self.list_url).json()]
        self.assertEqual(names, ["a.pdf"])

    def test_owner_downloads_via_api(self):
        alice = self.api_client(self.alice)
        doc_id = alice.post(self.list_url, {"file": pdf()}).json()["id"]
        response = alice.get(reverse("uploads:portal-api-download", args=[doc_id]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(b"".join(response.streaming_content), PDF_BYTES)

    def test_other_user_download_via_api_is_404(self):
        doc_id = self.api_client(self.alice).post(self.list_url, {"file": pdf()}).json()["id"]
        response = self.api_client(self.bob).get(reverse("uploads:portal-api-download", args=[doc_id]))
        self.assertEqual(response.status_code, 404)

    def test_anonymous_download_via_api_is_403(self):
        doc_id = self.api_client(self.alice).post(self.list_url, {"file": pdf()}).json()["id"]
        self.assertEqual(self.client.get(reverse("uploads:portal-api-download", args=[doc_id])).status_code, 403)

    def test_session_authenticated_post_needs_csrf_token(self):
        strict = Client(enforce_csrf_checks=True)
        strict.force_login(self.alice)
        self.assertEqual(strict.post(self.list_url, {"file": pdf()}).status_code, 403)


# ======================================================================= static files
class StaticFilesTests(TempStorageTestCase):
    def test_pages_link_the_collected_stylesheet(self):
        response = self.client.get(reverse("uploads:upload"))
        self.assertContains(response, '/static/uploads/css/site.css')

    def test_collectstatic_gathers_the_css(self):
        call_command("collectstatic", interactive=False, verbosity=0)
        self.assertTrue((self.tmp / "static" / "uploads" / "css" / "site.css").exists())

    def test_static_and_media_are_different_folders(self):
        from django.conf import settings
        self.assertNotEqual(settings.STATIC_ROOT, settings.MEDIA_ROOT)
        self.assertNotEqual(settings.PRIVATE_MEDIA_ROOT, settings.MEDIA_ROOT)
