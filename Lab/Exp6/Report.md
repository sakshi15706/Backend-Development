# Registration Form: Client-Side Validation

**Client-Side Scripts for Form Validation using JavaScript**

*Lab Experiment 6 Report*

Student: Sakshi Jaiswal | Sap Id: 590015706

## 1. Introduction and Objective

Form validation checks that the data a user enters is complete and correct before it is accepted. Client-side validation does this in the browser with JavaScript, so the user gets instant feedback without waiting for the server. This experiment builds a registration form that validates every field using JavaScript.

Objectives:

- Write client-side scripts that validate form input using JavaScript.
- Use regular expressions to check formats such as email and mobile number.
- Show clear error messages next to each field.
- Validate while the user types, when a field loses focus, and again on submit.
- Stop the form from being submitted while any field is invalid.

## 2. Technology Stack

| Component | Technology | Purpose |
|---|---|---|
| Structure | HTML5 | Form fields, labels and error placeholders |
| Styling | CSS3 | Layout, valid / invalid colours, light and dark theme |
| Logic | JavaScript (ES6) | Validation rules, events, DOM updates |
| Tools | VS Code, Chrome / Edge DevTools | Writing and testing the code |

## 3. How to Run

1. Keep `index.html` in a folder named `exp6-form-validation`.
2. Open it in Chrome or Edge (double-click it, or use the Live Server extension in VS Code).
3. No installation or server is needed.

## 4. Project Structure

```
exp6-form-validation/
├── index.html    # HTML, CSS and JavaScript in one file
└── REPORT.md     # This report
```

## 5. Working of the Application

### 5.1 Form Fields and Validation Rules

| Field | Rule | Example error message |
|---|---|---|
| Full name | Required; 3 to 50 characters; letters, spaces, `.` `'` `-` only | "Name can contain only letters and spaces." |
| Email | Required; must match the pattern `name@domain.tld` | "Enter a valid email, e.g. name@example.com." |
| Mobile number | Required; digits only; exactly 10 digits; starts with 6, 7, 8 or 9 | "Mobile number must be exactly 10 digits." |
| Date of birth | Required; not in the future; age at least 18 | "You must be at least 18 years old." |
| Gender | One radio button must be selected | "Please select a gender." |
| Country | A country must be chosen from the list | "Please select a country." |
| Password | At least 8 characters; uppercase, lowercase, digit and special character; no spaces | "Add at least one uppercase letter." |
| Confirm password | Required; must equal the password | "Passwords do not match." |
| Terms | Checkbox must be ticked | "You must accept the terms and conditions." |

### 5.2 Application Flow

```
User types / leaves a field
        |
        v
validateField(id) --> Validators[id](value) --> "" (valid) or error message
        |
        v
setState(id, message) --> shows red error / green border

User clicks Register
        |
        v
submit event --> preventDefault() --> validate ALL fields
        |
   +----+-----------------+
   |                      |
any invalid           all valid
focus first invalid   showSuccess() --> summary card
```

### 5.3 How each feature works

**Validators object.** All rules are in one object, `Validators`. Each function takes the field's value and returns an error message, or an empty string when the value is valid. Keeping the rules separate from the page code makes them easy to read and test.

```js
phone(v) {
  v = v.replace(/[\s-]/g, "");
  if (!v) return "Mobile number is required.";
  if (!/^\d+$/.test(v)) return "Mobile number can contain digits only.";
  if (v.length !== 10) return "Mobile number must be exactly 10 digits.";
  if (!/^[6-9]/.test(v)) return "Mobile number must start with 6, 7, 8 or 9.";
  return "";
}
```

**Regular expressions.** Patterns check formats: `^[^\s@]+@[^\s@]+\.[A-Za-z]{2,}$` for email, `/^\d+$/` for digits only, and `/[A-Z]/`, `/[a-z]/`, `/\d/`, `/[^A-Za-z0-9]/` for the password rules.

**When validation runs.** A field is validated when it loses focus (`blur`). After that, it is re-validated on every keystroke (`input`), so the error disappears as soon as the user fixes it. This avoids showing errors on fields the user has not touched yet.

**Submit handling.** The form has `novalidate`, so the browser's own pop-ups are turned off and JavaScript controls all messages. On submit, `e.preventDefault()` stops the page from sending, every field is validated, and focus moves to the first invalid field. Only if all fields pass is the success card shown.

**Password strength meter.** `passwordScore()` gives 0 to 4 points (length, upper and lower case, digit, special character), and the bar shows Weak, Fair, Good or Strong.

**Confirm password.** When the password changes, the confirm field is re-checked, so a mismatch is caught even if the user edits the first password last.

**Date of birth.** The `max` attribute is set to today's date, and the age is calculated from the date of birth, taking the month and day into account.

**Show / Hide password.** A button switches the input type between `password` and `text`.

**Safe output.** The summary on the success card is built with `textContent`, not `innerHTML`, so anything typed by the user cannot run as HTML or script. The password is never shown on the success card.

## 6. Testing

| Test | Expected Result |
|---|---|
| Click Register with an empty form | Every field shows its error; focus moves to Full name |
| Full name `Al` | "Name must be at least 3 characters." |
| Full name `Sak123` | "Name can contain only letters and spaces." |
| Email `abc` or `a@b` | Invalid email message |
| Email `sakshi@example.com` | Valid, green border |
| Mobile `12345` | "Mobile number must be exactly 10 digits." |
| Mobile `5123456789` | "Mobile number must start with 6, 7, 8 or 9." |
| Mobile `98765 43210` | Valid (space is ignored) |
| Date of birth in 2015 | "You must be at least 18 years old." |
| Date of birth in the future | Date picker blocks it; message if typed |
| Password `abcdefgh` | "Add at least one uppercase letter." |
| Password `Abcd@1234` | Valid; meter shows Strong |
| Confirm password different | "Passwords do not match." |
| Change password after confirming | Confirm field is re-checked automatically |
| Terms not ticked | "You must accept the terms and conditions." |
| All fields valid, click Register | Success card with a summary (no password) |
| Click Reset | Form, messages and strength meter are cleared |

Automated check: the 30 validator test cases (valid and invalid values for each field) were run in Node.js, and all 30 passed.

*Output:* *(screenshots: empty-form errors, partly valid form, password meter, success card)*

## 7. Problems Faced and Solutions

| Problem | Cause | Solution |
|---|---|---|
| Browser showed its own error pop-ups | HTML5 built-in validation was active | Added `novalidate` to the form so JavaScript controls the messages |
| Page reloaded on submit and the data disappeared | Default form submission | Called `e.preventDefault()` in the submit handler |
| Errors appeared before the user typed anything | Validation ran on page load or on focus | Validate on `blur` first, then on `input` only for touched fields |
| Confirm password stayed valid after changing the password | Only the confirm field was checked | Re-validate the confirm field whenever the password changes |
| Age was wrong around the birthday | Only the year was subtracted | Compared month and day as well |
| Radio group error could not be attached to one input | Radios share a name | Validated the group using the checked radio and showed one shared message |

*(Keep only the problems you actually faced.)*

## 8. Limitations and Future Scope

Current limitations:

- Client-side validation can be bypassed (by disabling JavaScript or sending a request directly), so it must never be the only check.
- The form does not send data anywhere; it only shows a success summary.
- The country list is short and fixed.
- Email format is checked, but whether the address really exists is not.

Possible improvements:

- Send the form to a server (for example Node.js and Express) and repeat all checks there.
- Check whether an email or username is already taken using AJAX.
- Add more fields such as address and PIN code, and use the HTML5 `pattern` attribute as a fallback.
- Add multi-language messages and screen-reader announcements for errors.

## 9. Conclusion

This experiment built a registration form validated entirely with client-side JavaScript. Rules for name, email, mobile number, date of birth, gender, country, password and terms were written as small functions that return error messages, using regular expressions where a format had to be checked. Validation runs on blur, on input and on submit, the form is blocked until every field is valid, and users get a password strength meter and show / hide option. It also showed that client-side validation improves user experience but must always be paired with server-side validation for security.
