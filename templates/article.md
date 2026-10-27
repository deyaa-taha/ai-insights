---
title: "Article title"
date: YYYY-MM-DD
lang: en            # en | he | ar
tags: [tag-one, tag-two]
summary: "One or two sentences. Shown in the README index and used as the SEO description."
series: ""          # optional, a slug from /series
translations:       # optional, sibling files of the same article
  he: index.he.md
  ar: index.ar.md
canonical_url: ""   # set when the article is also published on DeyaaTechLab
draft: true         # remove or set false to list it in the README
---

# Article title

> 🌐 **Read in:** English · [עברית](index.he.md) · [العربية](index.ar.md)

Hook: the problem in two or three sentences.

## Context

## The core idea

## In practice

## Takeaway

---

*Written by [Deyaa Taha](https://github.com/deyaa-taha).*

<!--
Usage:
1. Copy to articles/<YYYY>/<YYYY-MM>-<slug>/index.md
2. Images go next to it in ./images/
3. For Hebrew / Arabic: index.he.md / index.ar.md, wrap the body in <div dir="rtl" lang="he|ar"> ... </div>
   (leave a blank line after the opening tag and before the closing tag; keep code blocks outside the div)
4. Commit. The GitHub Action regenerates the README index.
-->
