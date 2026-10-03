# Experiment 1: Web Page with All Possible Elements of HTML5

**Session:** 1  
**Course Outcome:** CO2  
**Student:** Sakshi  
**Date:**  22 August 2026  
**File:** `index.html`

---

## 1. Aim

To create a web page that uses all the major elements of HTML5: text, semantic, list, table, multimedia, graphics, form and interactive elements.

## 2. Software Requirements

| Item | Details |
|---|---|
| Editor | Visual Studio Code |
| Browser | Google Chrome / Microsoft Edge / Firefox |
| Language | HTML5 (with a little CSS and JavaScript) |
| Extension (optional) | Live Server |

## 3. Theory

**HTML5** (HyperText Markup Language 5) is the latest standard markup language used to build the structure of a web page. It adds new features over older HTML versions:

- **Semantic elements** (`header`, `nav`, `main`, `section`, `article`, `aside`, `footer`) that describe the meaning of content.
- **Multimedia support** with `audio` and `video`, without needing plugins like Flash.
- **Graphics** with `canvas` and inline `svg`.
- **Better forms** with new input types (`email`, `date`, `color`, `range`, etc.), validation attributes and elements like `datalist`, `output`, `progress` and `meter`.
- **Interactive elements** such as `details`, `summary` and `dialog`.

Every HTML5 document starts with `<!DOCTYPE html>` and has a `<head>` (information about the page) and a `<body>` (visible content).

## 4. Elements Used in the Page

| Category | Elements |
|---|---|
| Document structure | `html`, `head`, `meta`, `title`, `base`, `style`, `body`, `script`, `noscript` |
| Page layout (semantic) | `header`, `nav`, `main`, `section`, `article`, `aside`, `footer`, `address` |
| Headings and paragraphs | `h1` to `h6`, `p`, `hr`, `br`, `wbr`, `pre`, `blockquote` |
| Text formatting | `b`, `strong`, `i`, `em`, `u`, `mark`, `small`, `del`, `ins`, `s`, `sub`, `sup` |
| Computer and special text | `code`, `kbd`, `samp`, `var`, `abbr`, `dfn`, `q`, `cite`, `time`, `data`, `bdo`, `bdi`, `ruby`, `rt`, `rp` |
| Lists | `ul`, `ol`, `li`, `dl`, `dt`, `dd`, `menu` |
| Links | `a` (external, internal, `mailto:`, `tel:`) |
| Tables | `table`, `caption`, `colgroup`, `col`, `thead`, `tbody`, `tfoot`, `tr`, `th`, `td` (with `colspan` and `rowspan`) |
| Images | `img`, `figure`, `figcaption`, `picture`, `source`, `map`, `area` |
| Audio and video | `audio`, `video`, `track` |
| Embedding | `iframe`, `embed`, `object` |
| Graphics | `canvas`, `svg` (`rect`, `circle`, `polygon`) |
| Forms | `form`, `fieldset`, `legend`, `label`, `input`, `textarea`, `select`, `optgroup`, `option`, `datalist`, `output`, `progress`, `meter`, `button` |
| Interactive | `details`, `summary`, `dialog`, `template` |

### Input types used

`text`, `email`, `password`, `number`, `tel`, `url`, `search`, `date`, `time`, `datetime-local`, `month`, `week`, `color`, `range`, `file`, `hidden`, `radio`, `checkbox`, `submit`, `reset`.

## 5. Procedure

1. Open VS Code and create a folder named `experiment1`.
2. Inside it, create a file named `index.html`.
3. Type `!` and press Tab to get the basic HTML5 structure (or write `<!DOCTYPE html>` manually).
4. Add the `meta` tags, `title` and a small `style` block in the `head`.
5. Add `header` with `nav` links in the `body`.
6. Inside `main`, create sections one by one: text, semantic elements, lists, tables, media, graphics, forms and interactive elements.
7. Add the `footer` and a `script` block for canvas drawing, the calculator and the dialog.
8. Save the file (`Ctrl + S`).
9. Run it: right-click `index.html` and choose **Open with Live Server**, or double-click the file to open it in a browser.
10. Check every section in the browser and note the output.

## 6. Structure of the Code

```
index.html
├── <head>      meta tags, title, CSS
└── <body>
    ├── <header> + <nav>
    ├── <main>
    │   ├── Section 1  Text formatting
    │   ├── Section 2  Semantic elements (article, aside, figure)
    │   ├── Section 3  Lists and links
    │   ├── Section 4  Table
    │   ├── Section 5  Multimedia (picture, map, audio, video, iframe)
    │   ├── Section 6  Graphics (canvas, svg)
    │   ├── Section 7  Form elements
    │   └── Section 8  Interactive elements
    ├── <footer>
    └── <script>   canvas, output calculation, dialog, template
```

### Key code snippets

**Basic structure**

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Experiment 1 - All HTML5 Elements</title>
</head>
<body> ... </body>
</html>
```

**Table with merged cells**

```html
<tr><td colspan="2">Merged two columns</td><td>--</td></tr>
<tr><td rowspan="2">Amit</td><td>HTML</td><td>25</td></tr>
```

**Canvas drawing**

```js
var ctx = document.getElementById("myCanvas").getContext("2d");
ctx.fillStyle = "#8e44ad";
ctx.fillRect(10, 10, 100, 100);
```

**Dialog box**

```html
<dialog id="myDialog">...</dialog>
<script>
  document.getElementById("openDialog").onclick = function () { dlg.showModal(); };
</script>
```

## 7. Output

Take a screenshot of the page in the browser and paste it here:

```
![Output of Experiment 1](screenshot.png)
```

The page shows, from top to bottom:

1. A dark header with the title and navigation links.
2. Text in different styles (bold, italic, highlighted, subscript, superscript, quotes, code, keyboard keys).
3. An article, an aside and an image with a caption.
4. Bulleted, numbered and description lists, and different types of links.
5. A table with a caption, merged cells, header and footer.
6. A responsive picture, a clickable image map, an audio player, a video player and embedded pages.
7. A canvas drawing and an SVG drawing.
8. A form with all input types, radio buttons, checkboxes, a drop-down, a datalist, a text area, a progress bar and a meter.
9. A collapsible `details` section, a pop-up dialog and a template button.
10. A footer with the copyright line.

## 8. Observations

- Semantic tags (`header`, `nav`, `main`, `footer`) divide the page clearly and make the code easier to read.
- New input types show date pickers, a colour picker and a slider in the browser. `email`, `url` and `tel` also validate the values.
- The `required` and `pattern` attributes stop the form from submitting with wrong data.
- `canvas` draws shapes using JavaScript, while `svg` draws shapes using markup.
- `audio` and `video` play without any plugin. They need an internet connection here because the files are online.
- `details` expands and collapses without JavaScript. `dialog` needs a small script to open and close.

## 9. Result

A web page demonstrating all the major HTML5 elements was created successfully, and every element displayed correctly in the browser.

## 10. Conclusion

HTML5 gives a complete set of elements for structure, text, media, graphics, forms and interaction. Semantic elements make pages meaningful and accessible, and built-in audio, video, canvas and form features reduce the need for external plugins and extra scripting.

## 11. Viva Questions

1. **What is HTML5?** The latest version of HTML, used to structure web pages. It adds semantic tags, audio, video, canvas and new form inputs.
2. **What is the use of `<!DOCTYPE html>`?** It tells the browser that the document is HTML5.
3. **What are semantic elements? Name some.** Elements whose names describe their purpose: `header`, `nav`, `section`, `article`, `aside`, `footer`.
4. **Difference between `<b>` and `<strong>`?** `<b>` only makes text bold. `<strong>` also means the text is important.
5. **Difference between `<i>` and `<em>`?** `<i>` only makes text italic. `<em>` also gives emphasis to the text.
6. **Difference between `canvas` and `svg`?** `canvas` is pixel-based and drawn with JavaScript. `svg` is vector-based and written in markup, so it does not lose quality when resized.
7. **What is the use of `<meta name="viewport">`?** It makes the page fit different screen sizes, which helps responsive design.
8. **What is the use of `datalist`?** It gives suggestions while typing in an input box.
9. **What does `colspan` do? What does `rowspan` do?** `colspan` merges cells across columns. `rowspan` merges cells across rows.
10. **Name some new input types in HTML5.** `email`, `date`, `color`, `range`, `number`, `url`, `tel`, `search`, `datetime-local`, `month`, `week`.
11. **Difference between `progress` and `meter`?** `progress` shows the completion of a task. `meter` shows a value within a known range, such as disk usage.
12. **What are `<details>` and `<summary>`?** They create a collapsible section. `summary` is the visible heading and `details` holds the hidden content.
13. **Difference between block and inline elements?** Block elements (`div`, `p`, `h1`) take the full width and start on a new line. Inline elements (`span`, `a`, `b`) take only the needed width.
14. **Which elements are used to add audio and video?** `<audio>` and `<video>`, with `<source>` for different file formats.
15. **What is the use of `<fieldset>` and `<legend>`?** `fieldset` groups related form fields. `legend` gives the group a title.
