<%
// Showcase listing template.
//
// Two hard-won constraints on how this is written — both cost a render to
// find, so please keep the shape:
//
//  1. A listing `template:` replaces the WHOLE listing, so it receives `items`
//     (plural) and iterates itself. A singular `item` exists only inside
//     Quarto's per-item partials; referencing one here is a ReferenceError.
//
//  2. Declarations must live in this top-level block. A `const` declared
//     inside the loop-opening tag is NOT visible to later output tags, so
//     everything the loop needs is a helper defined here and called inline.
//     (Quarto's own listing-grid.ejs.md follows the same pattern.)
//
// Each item supplies its own HTML through the `card` field in its front
// matter, so a card can be anything — a photo, a badge, an embed, a quote.

// Width in twelfths. `|| 4` catches both a missing field and a non-numeric
// one, since parseInt returns NaN there and NaN is falsy.
const cardWidth = (w) => Math.min(12, Math.max(1, parseInt(w, 10) || 4));

// Fall back card -> description so a half-written item still shows something.
const cardBody = (item) => item.card || item.description || "";

// Optional trailing link: the item's own `link`, else its generated page.
const cardLink = (item) => {
  const href = item.link || item.path || "";
  if (!item.title || !href) return "";
  return '<a class="showcase-card__link" href="' + href + '">' + item.title + "</a>";
};
%>

```{=html}
<% for (const item of items) { %>
<div class="showcase-card" style="--showcase-width: <%= cardWidth(item.width) %>;">
<%- cardBody(item) %>
<%- cardLink(item) %>
</div>
<% } %>
```
