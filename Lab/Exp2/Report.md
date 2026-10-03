# Experiment 2: Web Page with All Types of Cascading Style Sheets

**Session:** 2  
**Course Outcome:** CO2  
**Student:** Sakshi  
**Date:** 3 September 2026  
**Files:** `index.html`, `style.css`

---

## 1. Aim

To create a web page that uses all types of CSS (inline, internal and external) along with the main selectors, properties, layouts and effects.

## 2. Software Requirements

| Item | Details |
|---|---|
| Editor | Visual Studio Code |
| Browser | Google Chrome / Microsoft Edge / Firefox |
| Languages | HTML5 and CSS3 |
| Extension (optional) | Live Server |

## 3. Theory

**CSS (Cascading Style Sheets)** is used to control the look and layout of HTML pages: colours, fonts, spacing, positions and animations. It separates the content (HTML) from the design (CSS).

### Syntax

```css
selector {
  property: value;
}
```

### Types of CSS

| Type | Where it is written | Example | Use |
|---|---|---|---|
| **Inline** | In the `style` attribute of a tag | `<p style="color:red;">` | Styling one single element |
| **Internal** | In a `<style>` tag inside `<head>` | `<style> p { color: red; } </style>` | Styling one single page |
| **External** | In a separate `.css` file, linked with `<link>` | `<link rel="stylesheet" href="style.css">` | Styling many pages with one file |
| **Imported** | `@import` inside a CSS file or `<style>` | `@import url("extra.css");` | Loading one CSS file from another |

### Priority (cascade order)

Inline CSS > ID selector > Class selector > Element selector. If the specificity is equal, the rule written last wins. `!important` overrides everything.

## 4. Concepts Covered in the Page

### 4.1 Selectors

| Selector | Example | Meaning |
|---|---|---|
| Universal | `*` | Selects all elements |
| Element | `p` | Selects all `p` tags |
| Group | `h1, h2, h3` | Same style for many elements |
| Class | `.highlight` | Elements with `class="highlight"` |
| ID | `#unique-box` | The element with `id="unique-box"` |
| Descendant | `header h1` | `h1` anywhere inside `header` |
| Child | `.parent > p` | Only direct child `p` |
| Adjacent sibling | `h3 + p` | The `p` right after `h3` |
| General sibling | `.marker ~ p` | All `p` after `.marker` |
| Attribute | `input[type="text"]`, `a[href$=".pdf"]` | Elements with a given attribute |
| Pseudo-class | `a:hover`, `li:first-child`, `tr:nth-child(even)`, `input:focus` | Elements in a special state or position |
| Pseudo-element | `::first-letter`, `::first-line`, `::before`, `::after`, `::selection` | A part of an element |

### 4.2 Properties used

| Group | Properties |
|---|---|
| Colours | name, hex, `rgb()`, `rgba()`, `hsl()`, `linear-gradient()`, `radial-gradient()` |
| Text | `text-align`, `text-transform`, `text-decoration`, `letter-spacing`, `word-spacing`, `text-shadow`, `text-indent` |
| Font | `font-family`, `font-size`, `font-style`, `font-weight`, `font-variant` |
| Box model | `width`, `height`, `padding`, `margin`, `border`, `border-radius`, `box-sizing`, `box-shadow` |
| Display | `display` (inline, block, inline-block, none), `visibility`, `opacity`, `overflow`, `cursor` |
| Position | `static`, `relative`, `absolute`, `fixed`, `sticky`, `top`, `left`, `right`, `bottom`, `z-index` |
| Float | `float`, `clear` (clearfix) |
| Flexbox | `display: flex`, `justify-content`, `align-items`, `flex-wrap`, `gap`, `flex` |
| Grid | `display: grid`, `grid-template-columns`, `gap`, `grid-column` |
| Effects | `transform` (rotate, scale, skew, translate), `transition`, `@keyframes`, `animation` |
| Responsive | `@media (max-width: 700px)`, `@media print` |
| Variables | `:root { --primary: ... }` and `var(--primary)` |

### 4.3 The box model

Every element is a box made of four layers:

```
+--------------------------------+
|            MARGIN              |
|   +------------------------+   |
|   |        BORDER          |   |
|   |   +----------------+   |   |
|   |   |    PADDING     |   |   |
|   |   |   +--------+   |   |   |
|   |   |   |CONTENT |   |   |   |
|   |   |   +--------+   |   |   |
|   |   +----------------+   |   |
|   +------------------------+   |
+--------------------------------+
```

## 5. Procedure

1. Create a folder `experiment2` in VS Code.
2. Create `index.html` and add the HTML5 structure with a header, nav, main sections and footer.
3. Create `style.css` in the same folder.
4. In `index.html`, link the external CSS: `<link rel="stylesheet" href="style.css">`.
5. Add internal CSS in a `<style>` tag inside `<head>`.
6. Add inline CSS using the `style` attribute on one element.
7. Write CSS rules for selectors, colours, text, box model, display, position, float, flexbox and grid in `style.css`.
8. Add transforms, transitions, animations and media queries.
9. Save both files with `Ctrl + S`.
10. Open `index.html` with Live Server (or double-click it) and check each section.
11. Hover, click and resize the browser to test hover effects, focus styles, animations and responsiveness.

## 6. Structure of the Code

```
experiment2/
├── index.html    # inline CSS, internal CSS and the page content
└── style.css     # external CSS
```

### Key code snippets

**Inline CSS**

```html
<p style="color: white; background-color: #c0392b; padding: 10px;">Inline CSS</p>
```

**Internal CSS**

```html
<style>
  .internal-demo { background-color: #e8f8f5; color: #117a65; padding: 12px; }
</style>
```

**External CSS**

```html
<link rel="stylesheet" href="style.css">
```

**Flexbox**

```css
.flex-container { display: flex; justify-content: space-around; gap: 10px; }
```

**Grid**

```css
.grid-container { display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; }
```

**Animation**

```css
@keyframes slide {
  0%   { left: 0; }
  50%  { left: 200px; }
  100% { left: 0; }
}
.anim-box { position: absolute; animation: slide 4s infinite; }
```

**Media query**

```css
@media (max-width: 700px) {
  .grid-container { grid-template-columns: 1fr; }
}
```

## 7. Output

Take a screenshot of the page in the browser and paste it here:

```
![Output of Experiment 2](screenshot.png)
```

The page shows:

1. A gradient header, a dark navigation bar and sections in white cards with shadows.
2. Three paragraphs styled by inline, internal and external CSS.
3. Examples of every selector type, including attribute and pseudo selectors.
4. Text in different colours, fonts, alignments, decorations and shadows.
5. Boxes with different border styles, padding, margin, and gradient backgrounds.
6. Layout demos: display, position, float, flexbox and a 3-column grid.
7. Boxes that rotate, scale, skew and move on hover, a sliding animation and pulsing text.
8. A striped table and lists with different markers.
9. A fixed label at the bottom right corner of the screen.

## 8. Observations

- The inline style overrides the style of the same property given in internal or external CSS.
- A change in `style.css` changes the look of the whole page, so one file can control many pages.
- `:hover`, `:focus` and `:nth-child` change the look according to user action and position without any JavaScript.
- `position: fixed` keeps an element on the screen while scrolling, but `sticky` keeps it only while its section is visible.
- Flexbox arranges items in one direction (a row or a column), while Grid works in rows and columns together.
- When the browser is narrowed below 700px, the grid becomes one column and the flex items stack, because of the media query.

## 9. Result

A web page using inline, internal and external CSS with selectors, box model, layouts, transformations and animations was created successfully, and all styles were displayed correctly in the browser.

## 10. Conclusion

CSS separates design from content and makes web pages attractive, consistent and responsive. External CSS is best for large websites because one file styles many pages, internal CSS suits a single page, and inline CSS is useful for a quick change on one element.

## 11. Viva Questions

1. **What is CSS?** A language used to style HTML pages: colours, fonts, spacing and layout.
2. **What are the types of CSS?** Inline, internal and external (and imported using `@import`).
3. **Which type is best and why?** External CSS, because one file can style many pages and it is easy to maintain.
4. **Which CSS has the highest priority?** Inline CSS.
5. **Difference between class and ID selector?** A class (`.name`) can be used on many elements. An ID (`#name`) must be unique on a page.
6. **What is the box model?** Every element is a box made of content, padding, border and margin.
7. **Difference between padding and margin?** Padding is the space inside the border. Margin is the space outside the border.
8. **Difference between `display: none` and `visibility: hidden`?** `none` removes the element and its space. `hidden` hides it but keeps its space.
9. **Name the position values.** `static`, `relative`, `absolute`, `fixed`, `sticky`.
10. **Difference between `relative` and `absolute` position?** `relative` moves the element from its normal place. `absolute` positions it with respect to the nearest positioned parent.
11. **What is Flexbox? What is Grid?** Flexbox is a one-dimensional layout (row or column). Grid is a two-dimensional layout (rows and columns).
12. **What is a pseudo-class? What is a pseudo-element?** A pseudo-class selects an element in a state (`:hover`). A pseudo-element selects a part of an element (`::first-letter`).
13. **What is the difference between transition and animation?** A transition changes from one state to another when triggered (like hover). An animation uses `@keyframes` and can run on its own and repeat.
14. **What is a media query?** A rule that applies styles only for certain screen sizes, used for responsive design.
15. **What does `box-sizing: border-box` do?** It includes padding and border in the width and height of the element.
16. **What are CSS variables?** Custom values like `--primary: #2c3e50;` defined once and reused with `var(--primary)`.
