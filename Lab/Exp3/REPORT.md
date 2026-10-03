# Experiment 3: Responsive Web Page with HTML and CSS

**Session:** 3  
**Course Outcome:** CO2  
**Student:** Sakshi  
**Date:** 12 September 2026  
**Files:** `index.html`, `style.css`

---

## 1. Aim

To create a responsive web page using HTML and CSS that adjusts its layout automatically to mobile, tablet, laptop and large-screen devices.

## 2. Software Requirements

| Item | Details |
|---|---|
| Editor | Visual Studio Code |
| Browser | Google Chrome / Microsoft Edge (with Developer Tools) |
| Languages | HTML5 and CSS3 |
| Extension (optional) | Live Server |

## 3. Theory

**Responsive Web Design (RWD)** is an approach in which a web page changes its layout according to the size of the screen, so the same page works well on phones, tablets, laptops and desktops.

### Main building blocks

| Building block | Meaning | Used in this page |
|---|---|---|
| **Viewport meta tag** | Tells the mobile browser to use the device width and not zoom out | `<meta name="viewport" content="width=device-width, initial-scale=1.0">` |
| **Flexible (fluid) layout** | Sizes in `%`, `fr`, `rem` instead of fixed pixels | `width: 100%`, `1fr`, `rem` font sizes |
| **Flexible images** | Images shrink with the container | `img { max-width: 100%; height: auto; }` |
| **Media queries** | Apply CSS only when screen conditions match | `@media (min-width: 601px) { ... }` |
| **Flexbox and Grid** | Layouts that rearrange themselves | `display: flex`, `display: grid` |

### Mobile-first approach

The base CSS is written for the smallest screen (one column). Then `min-width` media queries add more columns and features as the screen gets larger. This keeps the CSS simple and makes the page load well on phones.

### Breakpoints used

| Screen | Width | Layout |
|---|---|---|
| Mobile | up to 600px | 1 column, hamburger menu |
| Tablet | 601px and above | 2 columns |
| Laptop | 901px and above | 4 cards, full menu in a row |
| Large screen | 1200px and above | Bigger text and spacing |

## 4. Features of the Page

| Section | Responsive behaviour |
|---|---|
| **Header and navigation** | On mobile, a hamburger icon (&#9776;) opens and closes the menu (checkbox trick, no JavaScript). On 901px and above, the full menu shows in a row. The header is sticky. |
| **Hero** | Padding and heading size increase with the screen size. |
| **About** | Two columns stack vertically on mobile and sit side by side from 601px. |
| **Services cards** | 1 column on mobile, 2 columns on tablet, 4 columns on laptop (CSS Grid). |
| **Images** | `max-width: 100%` keeps images inside the screen. The gallery has 1, 2 and 3 columns. The `<picture>` element loads a different image for wide screens. |
| **Table** | Wrapped in a container with `overflow-x: auto`, so it scrolls sideways on small screens instead of breaking the layout. |
| **Contact form** | Name and email fields stack on mobile and sit side by side from 601px. |
| **Footer** | 1, 2 and 3 columns according to the screen width. |
| **Screen info** | A small script shows the current window width in the footer. |
| **Print and landscape** | Special rules for printing and for phones held sideways. |

## 5. Procedure

1. Create a folder `experiment3` in VS Code.
2. Create `index.html` and `style.css` in it.
3. In `index.html`, write the HTML5 structure and add the **viewport meta tag**.
4. Link the CSS file: `<link rel="stylesheet" href="style.css">`.
5. Create the sections: header with navigation, hero, about, services cards, gallery, table, contact form and footer.
6. In `style.css`, write the base (mobile) styles first.
7. Make images flexible with `max-width: 100%` and `height: auto`.
8. Use Flexbox and Grid for the layouts.
9. Add media queries with `min-width` for 601px, 901px and 1200px.
10. Save the files and open `index.html` with Live Server.
11. Test it: press `F12` in the browser, click the **device toolbar** icon (or `Ctrl + Shift + M`), and select Mobile, Tablet and Laptop sizes. You can also drag the window to make it narrower.
12. Take screenshots of each size.

## 6. Structure of the Code

```
experiment3/
├── index.html    # structure, viewport meta tag, hamburger menu, content
└── style.css     # mobile-first styles and media queries
```

### Key code snippets

**Viewport meta tag**

```html
<meta name="viewport" content="width=device-width, initial-scale=1.0">
```

**Flexible images**

```css
img { max-width: 100%; height: auto; display: block; }
```

**Cards: 1, 2 and 4 columns**

```css
.cards { display: grid; grid-template-columns: 1fr; gap: 16px; }          /* mobile */

@media (min-width: 601px) {
  .cards { grid-template-columns: repeat(2, 1fr); }                       /* tablet */
}
@media (min-width: 901px) {
  .cards { grid-template-columns: repeat(4, 1fr); }                       /* laptop */
}
```

**Hamburger menu without JavaScript**

```css
#menu-toggle { display: none; }
.nav { display: none; }
#menu-toggle:checked ~ .nav { display: flex; }      /* menu opens when checked */

@media (min-width: 901px) {
  .menu-icon { display: none; }
  .nav { display: flex; flex-direction: row; }       /* full menu on large screens */
}
```

**Scrollable table**

```css
.table-wrap { overflow-x: auto; }
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
| **Mobile (below 600px)** | Hamburger menu, one-column cards, stacked about boxes, one-column gallery, stacked form fields, one-column footer |
| **Tablet (601px to 900px)** | Hamburger menu, two-column cards and gallery, side-by-side about boxes and form fields, two-column footer |
| **Laptop (901px and above)** | Full menu in a row, four cards in one row, three-column gallery, three-column footer |

## 8. Observations

- Without the viewport meta tag, a phone shows the page as a zoomed-out desktop page. With it, the layout fits the phone screen.
- Images never overflow the screen because of `max-width: 100%`.
- The same HTML shows different layouts, because only the CSS rules change at each breakpoint.
- Grid with `repeat()` and `1fr` makes columns share the space equally, and only the number of columns changes in each media query.
- The hamburger menu works through the `:checked` selector, without any JavaScript.
- The table does not break the page on mobile; it scrolls horizontally inside its box.

## 9. Result

A responsive web page was created using HTML and CSS. Its layout adapted correctly to mobile, tablet, laptop and large screens.

## 10. Conclusion

Responsive design lets one web page serve all devices. The viewport meta tag, flexible images, Flexbox or Grid and media queries are the four main tools. Writing the CSS mobile first keeps the code simple, because the larger layouts are only added when the screen is wide enough.
