# Overleaf assets

This folder contains a draft write-up for Sections 3.1/3.2 and generated JPEG assets (figures + tables) you can upload into Overleaf.

## Generate JPEGs (locally)

From the repo root:
```bash
python3 overleaf/build_overleaf_assets.py
python3 overleaf/render_jpegs.py
```

This writes images to `overleaf/jpeg/`:
- `overleaf/jpeg/time_analysis.jpg`
- `overleaf/jpeg/time_analysis_100000_linear.jpg`
- `overleaf/jpeg/quality_analysis.jpg`
- `overleaf/jpeg/fit_percentage.jpg`
- `overleaf/jpeg/class_scale_table.jpg`
- `overleaf/jpeg/optimality_table.jpg`

## Upload to Overleaf

Upload the four JPEGs above into your Overleaf project (keep the paths, or adjust your `\includegraphics{...}` accordingly).

If you want the write-up text too, also upload:
- `overleaf/sections/section3.tex`

## Include in your Overleaf main `.tex`

Add these packages:
```tex
\usepackage{graphicx}
```

Include the write-up text (optional):
```tex
\input{overleaf/sections/section3.tex}
```

Insert a JPEG figure:
```tex
\begin{figure}[t]
  \centering
  \includegraphics[width=\linewidth]{overleaf/jpeg/time_analysis.jpg}
  \caption{Scheduling runtime as the number of classes increases.}
\end{figure}
```
