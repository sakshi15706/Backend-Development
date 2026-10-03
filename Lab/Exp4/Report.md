# Experiment 4: Responsive Web Page with Bootstrap

**Session:** 4  
**Course Outcome:** CO2  
**Student:** Sakshi  
**Date:** 16 September 2026  
**Files:** `index.html`, `style.css`

---

## 1. Aim

To create a responsive web page using the Bootstrap framework.

## 2. Software Requirements

| Item | Details |
|---|---|
| Editor | Visual Studio Code |
| Browser | Google Chrome / Microsoft Edge (with Developer Tools) |
| Framework | Bootstrap 5.3 (through CDN) |
| Internet | Required, because Bootstrap CSS, JS and icons load from a CDN |
| Extension (optional) | Live Server |

## 3. Theory

**Bootstrap** is a free, open-source front-end framework. It gives ready-made CSS classes and JavaScript components for building responsive, mobile-first websites quickly, without writing everything from scratch.

### Main features

| Feature | Description |
|---|---|
| **Grid system** | The page is divided into 12 columns. Classes like `col-md-6` decide how many columns an element takes on a screen size. |
| **Responsive breakpoints** | Predefined screen sizes: `sm`, `md`, `lg`, `xl`, `xxl`. |
| **Components** | Ready-made navbar, cards, buttons, alerts, modal, carousel, accordion, dropdown, forms and more. |
| **Utility classes** | Small classes for spacing (`mt-3`, `p-4`), colours (`bg-dark`, `text-white`), alignment (`text-center`), display (`d-none`, `d-flex`) and more. |
| **Mobile first** | Styles are written for small screens first and scale up. |
| **JavaScript plugins** | Navbar toggle, modal, carousel, etc. work through `data-bs-*` attributes with no extra code. |

### Bootstrap breakpoints

| Class prefix | Screen width | Device |
|---|---|---|
| `col-` | below 576px | Extra small (phones) |
| `col-sm-` | 576px and above | Small |
| `col-md-` | 768px and above | Medium (tablets) |
| `col-lg-` | 992px and above | Large (laptops) |
| `col-xl-` | 1200px and above | Extra large |
| `col-xxl-` | 1400px and above | Extra extra large |

### How to add Bootstrap (CDN)

```html
<!-- In <head> -->
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">

<!-- Before </body> -->
<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js"></script>
```

The viewport meta tag is also required:

```html
<meta name="viewport" content="width=device-width, initial-scale=1">
```

## 4. Features of the Page

| Section | Bootstrap classes and components used |
|---|---|
| **Navbar** | `navbar`, `navbar-expand-lg`, `navbar-toggler`, `collapse`, `dropdown`, `sticky-top`. It becomes a hamburger menu on screens smaller than 992px. |
| **Hero** | `text-center`, `text-white`, `display-4`, `lead`, `btn btn-light btn-lg` |
| **Grid and cards** | `container`, `row`, `g-4`, `col-12 col-sm-6 col-lg-3`, `card`, `card-body`, `h-100`, `shadow-sm`. 1 card per row on phones, 2 on tablets, 4 on laptops. |
| **Image and text layout** | `col-md-6`, `img-fluid`, `rounded`, `align-items-center`. Side by side on medium screens, stacked on mobile. |
| **Buttons** | `btn btn-primary`, `btn-success`, `btn-danger`, `btn-outline-dark`, `btn-sm`, `btn-lg` |
| **Alerts** | `alert alert-success`, `alert-warning alert-dismissible` (with a close button) |
| **Badges and progress** | `badge`, `rounded-pill`, `progress`, `progress-bar-striped`, `progress-bar-animated` |
| **Accordion** | `accordion`, `accordion-item`, `accordion-button`, `accordion-collapse` |
| **Carousel** | `carousel slide`, `carousel-inner`, `carousel-item`, controls and indicators |
| **Modal** | `modal fade`, `modal-dialog`, `modal-content`, opened by `data-bs-toggle="modal"` |
| **Table** | `table-responsive`, `table table-striped table-hover table-bordered`, `table-dark` |
| **Responsive utilities** | `d-none`, `d-sm-block`, `d-md-block` and so on, to show or hide text by screen size |
| **Form** | `form-control`, `form-select`, `form-check`, `form-label`, `col-md-6` for two-column fields |
| **Footer** | `bg-dark`, `text-white`, `row`, `col-md-4`, Bootstrap Icons |
| **Custom CSS** | `style.css`: gradient hero, hover lift on cards, carousel slide colours |

## 5. Procedure

1. Create a folder `experiment4` in VS Code.
2. Create `index.html` and `style.css` in it.
3. Write the HTML5 structure and add the viewport meta tag.
4. Add the Bootstrap CSS link (and Bootstrap Icons link) in `<head>`.
5. Add the Bootstrap JS bundle script before `</body>`.
6. Build the navbar with a toggler button for small screens.
7. Add the hero section, then the grid with cards using `container`, `row` and `col-*` classes.
8. Add the components: buttons, alerts, accordion, carousel and modal.
9. Add a responsive table inside `table-responsive`, and a form using Bootstrap form classes.
10. Add the footer.
11. Add a few extra styles in `style.css` and link it after Bootstrap.
12. Save the files and open `index.html` with Live Server (internet must be on).
13. Press `F12`, then `Ctrl + Shift + M`, and test on Mobile, Tablet and Laptop sizes.
14. Take screenshots.

## 6. Structure of the Code

```
experiment4/
├── index.html    # page using Bootstrap classes and components (CDN)
└── style.css     # small custom CSS added after Bootstrap
```

### Key code snippets

**Responsive grid of cards**

```html
<div class="container">
  <div class="row g-4">
    <div class="col-12 col-sm-6 col-lg-3">
      <div class="card h-100 text-center shadow-sm">
        <div class="card-body">...</div>
      </div>
    </div>
    <!-- more columns -->
  </div>
</div>
```

**Navbar with hamburger**

```html
<nav class="navbar navbar-expand-lg navbar-dark bg-dark sticky-top">
  <div class="container">
    <a class="navbar-brand" href="#">BootSite</a>
    <button class="navbar-toggler" data-bs-toggle="collapse" data-bs-target="#mainNav">
      <span class="navbar-toggler-icon"></span>
    </button>
    <div class="collapse navbar-collapse" id="mainNav"> ...links... </div>
  </div>
</nav>
```

**Responsive table**

```html
<div class="table-responsive">
  <table class="table table-striped table-hover"> ... </table>
</div>
```

**Modal**

```html
<button class="btn btn-dark" data-bs-toggle="modal" data-bs-target="#demoModal">Open Modal</button>
<div class="modal fade" id="demoModal"> ... </div>
```

## 7. Output

Take screenshots in the browser for different sizes and paste them here:

```
![Mobile view](mobile.png)
![Tablet view](tablet.png)
![Laptop view](laptop.png)
```

| Screen | What you see |
|---|---|
| **Mobile (below 576px)** | Hamburger menu, 1 card per row, image above text, stacked form fields, stacked footer |
| **Tablet (768px)** | Hamburger menu, 2 cards per row, image and text side by side, two-column form |
| **Laptop (992px and above)** | Full menu in a row, 4 cards in one row, three-column footer |

## 8. Observations

- Bootstrap produced a good-looking, responsive page with very little custom CSS, only by adding classes to the HTML.
- The 12-column grid with `col-12 col-sm-6 col-lg-3` changed the number of cards per row without any media query written by hand.
- The navbar, modal, carousel and accordion worked through `data-bs-*` attributes, without writing any JavaScript.
- `img-fluid` and `table-responsive` stopped images and tables from overflowing on small screens.
- Without the Bootstrap JS bundle, the hamburger menu, modal, carousel and dropdown do not work.
- The page needs internet, because Bootstrap is loaded from a CDN.

## 9. Result

A responsive web page was created using Bootstrap 5, and its layout and components worked correctly on mobile, tablet and laptop screen sizes.

## 10. Conclusion

Bootstrap speeds up web development because its grid system, ready-made components and utility classes handle most of the responsive design. Compared with plain CSS (Experiment 3), the same responsive result needed much less code, and the components with JavaScript worked without writing any script.

## 11. Viva Questions

1. **What is Bootstrap?** A free front-end framework with ready-made CSS and JavaScript for building responsive, mobile-first websites.
2. **How do you add Bootstrap to a page?** Through CDN links for the CSS in `<head>` and the JS bundle before `</body>`, or by downloading the files.
3. **What is the Bootstrap grid system?** A layout system that divides the page into 12 columns using `container`, `row` and `col-*` classes.
4. **What are the breakpoints in Bootstrap 5?** `sm` (576px), `md` (768px), `lg` (992px), `xl` (1200px) and `xxl` (1400px).
5. **Difference between `container` and `container-fluid`?** `container` has a fixed maximum width at each breakpoint. `container-fluid` always takes the full width.
6. **What does `col-md-6` mean?** The element takes 6 of 12 columns (half the width) on medium screens and above, and stacks full width on smaller screens.
7. **What is `col-12 col-sm-6 col-lg-3`?** Full width on phones, half on small screens, and one quarter (4 per row) on large screens.
8. **How do you make an image responsive in Bootstrap?** Add the class `img-fluid`.
9. **How do you make a table responsive?** Wrap the table in a `div` with class `table-responsive`.
10. **What is `navbar-expand-lg`?** The navbar shows the full menu on large screens and collapses into a hamburger menu on smaller screens.
11. **What are `data-bs-toggle` and `data-bs-target`?** Attributes that let Bootstrap's JavaScript open a modal, collapse or dropdown without writing script.
12. **What are utility classes? Give examples.** Small classes for common styles, like `mt-3` (margin), `p-4` (padding), `text-center`, `bg-dark`, `d-none`.
13. **What do the classes `d-none d-md-block` do?** They hide the element on small screens and show it from medium screens upwards.
14. **What is the use of the `g-4` class?** It sets the gap (gutter) between grid columns.
15. **Difference between Bootstrap and plain CSS?** Bootstrap gives pre-written, tested classes and components, so pages are built faster. Plain CSS gives full control but needs more code.
16. **Why is the Bootstrap JS bundle needed?** For interactive components like the navbar toggle, modal, carousel, accordion and dropdown. The bundle includes Popper, which dropdowns need.
17. **What are the disadvantages of Bootstrap?** Sites can look alike, the CSS file is large, and overriding default styles takes extra effort.
