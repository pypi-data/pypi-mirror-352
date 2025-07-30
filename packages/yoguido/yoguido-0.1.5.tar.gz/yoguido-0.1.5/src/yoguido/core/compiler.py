"""
Fixed YoGuido Compiler with Working Button Events
Replace your yoguido/core/compiler.py with this version
"""

import json
import subprocess
from pathlib import Path
from typing import Dict, List, Any

class YoGuidoCompiler:
    """
    Fixed Vanilla JavaScript compiler for YoGuido framework
    """
    
    def __init__(self, output_dir: str = "./yoguido_build"):
        self.output_dir = Path(output_dir)
        self.components = {}
        self.state_classes = {}
        self.css_built = False

    def compile_project(self, app_title: str = "YoGuido App"):
        """Compile entire project with CSS build integration"""
        self.output_dir.mkdir(exist_ok=True, parents=True)
        
        print(f"🔨 Compiling YoGuido app: {app_title}")
        
        # 1. Try to build Tailwind CSS
        self._generate_css()
        
        # 2. Analyze registered components
        self._analyze_components()
        
        # 3. Generate HTML file
        self._generate_html(app_title)
        
        # 4. Generate JavaScript
        self._generate_javascript()
        
        print(f"✅ Compilation complete!")
        print(f"   📁 Output directory: {self.output_dir}")
        print(f"   🌐 Open: {self.output_dir}/index.html")
        
        # Show CSS info
        css_file = self.output_dir / "styles.css"
        if css_file.exists():
            size_kb = css_file.stat().st_size / 1024
            print(f"   📏 CSS file size: {size_kb:.1f} KB")

    def _generate_css(self) -> bool:
        """Try to build Tailwind CSS"""
        css_input = """
/*! tailwindcss v4.1.8 | MIT License | https://tailwindcss.com */
@layer properties;
@layer theme, base, components, utilities;
@layer theme {
  :root, :host {
    --font-sans: ui-sans-serif, system-ui, sans-serif, "Apple Color Emoji",
      "Segoe UI Emoji", "Segoe UI Symbol", "Noto Color Emoji";
    --font-mono: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono",
      "Courier New", monospace;
    --color-red-50: oklch(97.1% 0.013 17.38);
    --color-red-100: oklch(93.6% 0.032 17.717);
    --color-red-200: oklch(88.5% 0.062 18.334);
    --color-red-300: oklch(80.8% 0.114 19.571);
    --color-red-500: oklch(63.7% 0.237 25.331);
    --color-red-600: oklch(57.7% 0.245 27.325);
    --color-red-700: oklch(50.5% 0.213 27.518);
    --color-red-800: oklch(44.4% 0.177 26.899);
    --color-orange-50: oklch(98% 0.016 73.684);
    --color-orange-200: oklch(90.1% 0.076 70.697);
    --color-yellow-50: oklch(98.7% 0.026 102.212);
    --color-yellow-100: oklch(97.3% 0.071 103.193);
    --color-yellow-200: oklch(94.5% 0.129 101.54);
    --color-yellow-800: oklch(47.6% 0.114 61.907);
    --color-green-50: oklch(98.2% 0.018 155.826);
    --color-green-100: oklch(96.2% 0.044 156.743);
    --color-green-200: oklch(92.5% 0.084 155.995);
    --color-green-300: oklch(87.1% 0.15 154.449);
    --color-green-500: oklch(72.3% 0.219 149.579);
    --color-green-600: oklch(62.7% 0.194 149.214);
    --color-green-700: oklch(52.7% 0.154 150.069);
    --color-green-800: oklch(44.8% 0.119 151.328);
    --color-cyan-600: oklch(60.9% 0.126 221.723);
    --color-blue-50: oklch(97% 0.014 254.604);
    --color-blue-100: oklch(93.2% 0.032 255.585);
    --color-blue-200: oklch(88.2% 0.059 254.128);
    --color-blue-600: oklch(54.6% 0.245 262.881);
    --color-blue-800: oklch(42.4% 0.199 265.638);
    --color-indigo-600: oklch(51.1% 0.262 276.966);
    --color-purple-50: oklch(97.7% 0.014 308.299);
    --color-purple-100: oklch(94.6% 0.033 307.174);
    --color-purple-200: oklch(90.2% 0.063 306.703);
    --color-purple-500: oklch(62.7% 0.265 303.9);
    --color-purple-600: oklch(55.8% 0.288 302.321);
    --color-purple-700: oklch(49.6% 0.265 301.924);
    --color-gray-50: oklch(98.5% 0.002 247.839);
    --color-gray-100: oklch(96.7% 0.003 264.542);
    --color-gray-200: oklch(92.8% 0.006 264.531);
    --color-gray-300: oklch(87.2% 0.01 258.338);
    --color-gray-400: oklch(70.7% 0.022 261.325);
    --color-gray-500: oklch(55.1% 0.027 264.364);
    --color-gray-600: oklch(44.6% 0.03 256.802);
    --color-gray-700: oklch(37.3% 0.034 259.733);
    --color-gray-800: oklch(27.8% 0.033 256.848);
    --color-gray-900: oklch(21% 0.034 264.665);
    --color-black: #000;
    --color-white: #fff;
    --spacing: 0.25rem;
    --container-sm: 24rem;
    --container-md: 28rem;
    --container-4xl: 56rem;
    --container-7xl: 80rem;
    --text-xs: 0.75rem;
    --text-xs--line-height: calc(1 / 0.75);
    --text-sm: 0.875rem;
    --text-sm--line-height: calc(1.25 / 0.875);
    --text-base: 1rem;
    --text-base--line-height: calc(1.5 / 1);
    --text-lg: 1.125rem;
    --text-lg--line-height: calc(1.75 / 1.125);
    --text-xl: 1.25rem;
    --text-xl--line-height: calc(1.75 / 1.25);
    --text-2xl: 1.5rem;
    --text-2xl--line-height: calc(2 / 1.5);
    --text-3xl: 1.875rem;
    --text-3xl--line-height: calc(2.25 / 1.875);
    --font-weight-medium: 500;
    --font-weight-semibold: 600;
    --font-weight-bold: 700;
    --tracking-wider: 0.05em;
    --radius-md: 0.375rem;
    --radius-lg: 0.5rem;
    --radius-xl: 0.75rem;
    --ease-out: cubic-bezier(0, 0, 0.2, 1);
    --ease-in-out: cubic-bezier(0.4, 0, 0.2, 1);
    --animate-spin: spin 1s linear infinite;
    --animate-pulse: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
    --blur-sm: 8px;
    --default-transition-duration: 150ms;
    --default-transition-timing-function: cubic-bezier(0.4, 0, 0.2, 1);
    --default-font-family: var(--font-sans);
    --default-mono-font-family: var(--font-mono);
  }
}
@layer base {
  *, ::after, ::before, ::backdrop, ::file-selector-button {
    box-sizing: border-box;
    margin: 0;
    padding: 0;
    border: 0 solid;
  }
  html, :host {
    line-height: 1.5;
    -webkit-text-size-adjust: 100%;
    tab-size: 4;
    font-family: var(--default-font-family, ui-sans-serif, system-ui, sans-serif, "Apple Color Emoji", "Segoe UI Emoji", "Segoe UI Symbol", "Noto Color Emoji");
    font-feature-settings: var(--default-font-feature-settings, normal);
    font-variation-settings: var(--default-font-variation-settings, normal);
    -webkit-tap-highlight-color: transparent;
  }
  hr {
    height: 0;
    color: inherit;
    border-top-width: 1px;
  }
  abbr:where([title]) {
    -webkit-text-decoration: underline dotted;
    text-decoration: underline dotted;
  }
  h1, h2, h3, h4, h5, h6 {
    font-size: inherit;
    font-weight: inherit;
  }
  a {
    color: inherit;
    -webkit-text-decoration: inherit;
    text-decoration: inherit;
  }
  b, strong {
    font-weight: bolder;
  }
  code, kbd, samp, pre {
    font-family: var(--default-mono-font-family, ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace);
    font-feature-settings: var(--default-mono-font-feature-settings, normal);
    font-variation-settings: var(--default-mono-font-variation-settings, normal);
    font-size: 1em;
  }
  small {
    font-size: 80%;
  }
  sub, sup {
    font-size: 75%;
    line-height: 0;
    position: relative;
    vertical-align: baseline;
  }
  sub {
    bottom: -0.25em;
  }
  sup {
    top: -0.5em;
  }
  table {
    text-indent: 0;
    border-color: inherit;
    border-collapse: collapse;
  }
  :-moz-focusring {
    outline: auto;
  }
  progress {
    vertical-align: baseline;
  }
  summary {
    display: list-item;
  }
  ol, ul, menu {
    list-style: none;
  }
  img, svg, video, canvas, audio, iframe, embed, object {
    display: block;
    vertical-align: middle;
  }
  img, video {
    max-width: 100%;
    height: auto;
  }
  button, input, select, optgroup, textarea, ::file-selector-button {
    font: inherit;
    font-feature-settings: inherit;
    font-variation-settings: inherit;
    letter-spacing: inherit;
    color: inherit;
    border-radius: 0;
    background-color: transparent;
    opacity: 1;
  }
  :where(select:is([multiple], [size])) optgroup {
    font-weight: bolder;
  }
  :where(select:is([multiple], [size])) optgroup option {
    padding-inline-start: 20px;
  }
  ::file-selector-button {
    margin-inline-end: 4px;
  }
  ::placeholder {
    opacity: 1;
  }
  @supports (not (-webkit-appearance: -apple-pay-button))  or (contain-intrinsic-size: 1px) {
    ::placeholder {
      color: currentcolor;
      @supports (color: color-mix(in lab, red, red)) {
        color: color-mix(in oklab, currentcolor 50%, transparent);
      }
    }
  }
  textarea {
    resize: vertical;
  }
  ::-webkit-search-decoration {
    -webkit-appearance: none;
  }
  ::-webkit-date-and-time-value {
    min-height: 1lh;
    text-align: inherit;
  }
  ::-webkit-datetime-edit {
    display: inline-flex;
  }
  ::-webkit-datetime-edit-fields-wrapper {
    padding: 0;
  }
  ::-webkit-datetime-edit, ::-webkit-datetime-edit-year-field, ::-webkit-datetime-edit-month-field, ::-webkit-datetime-edit-day-field, ::-webkit-datetime-edit-hour-field, ::-webkit-datetime-edit-minute-field, ::-webkit-datetime-edit-second-field, ::-webkit-datetime-edit-millisecond-field, ::-webkit-datetime-edit-meridiem-field {
    padding-block: 0;
  }
  :-moz-ui-invalid {
    box-shadow: none;
  }
  button, input:where([type="button"], [type="reset"], [type="submit"]), ::file-selector-button {
    appearance: button;
  }
  ::-webkit-inner-spin-button, ::-webkit-outer-spin-button {
    height: auto;
  }
  [hidden]:where(:not([hidden="until-found"])) {
    display: none !important;
  }
}
@layer utilities {
  .absolute {
    position: absolute;
  }
  .fixed {
    position: fixed;
  }
  .relative {
    position: relative;
  }
  .static {
    position: static;
  }
  .inset-0 {
    inset: calc(var(--spacing) * 0);
  }
  .inset-y-0 {
    inset-block: calc(var(--spacing) * 0);
  }
  .top-1 {
    top: calc(var(--spacing) * 1);
  }
  .top-1\/2 {
    top: calc(1/2 * 100%);
  }
  .top-4 {
    top: calc(var(--spacing) * 4);
  }
  .right-0 {
    right: calc(var(--spacing) * 0);
  }
  .right-4 {
    right: calc(var(--spacing) * 4);
  }
  .left-0 {
    left: calc(var(--spacing) * 0);
  }
  .left-3 {
    left: calc(var(--spacing) * 3);
  }
  .z-50 {
    z-index: 50;
  }
  .mx-auto {
    margin-inline: auto;
  }
  .mt-2 {
    margin-top: calc(var(--spacing) * 2);
  }
  .mt-8 {
    margin-top: calc(var(--spacing) * 8);
  }
  .mb-4 {
    margin-bottom: calc(var(--spacing) * 4);
  }
  .block {
    display: block;
  }
  .flex {
    display: flex;
  }
  .inline-block {
    display: inline-block;
  }
  .inline-flex {
    display: inline-flex;
  }
  .table {
    display: table;
  }
  .table-cell {
    display: table-cell;
  }
  .table-row {
    display: table-row;
  }
  .h-2 {
    height: calc(var(--spacing) * 2);
  }
  .h-4 {
    height: calc(var(--spacing) * 4);
  }
  .h-5 {
    height: calc(var(--spacing) * 5);
  }
  .h-6 {
    height: calc(var(--spacing) * 6);
  }
  .h-10 {
    height: calc(var(--spacing) * 10);
  }
  .h-16 {
    height: calc(var(--spacing) * 16);
  }
  .h-64 {
    height: calc(var(--spacing) * 64);
  }
  .max-h-screen {
    max-height: 100vh;
  }
  .w-2 {
    width: calc(var(--spacing) * 2);
  }
  .w-5 {
    width: calc(var(--spacing) * 5);
  }
  .w-6 {
    width: calc(var(--spacing) * 6);
  }
  .w-10 {
    width: calc(var(--spacing) * 10);
  }
  .w-24 {
    width: calc(var(--spacing) * 24);
  }
  .w-56 {
    width: calc(var(--spacing) * 56);
  }
  .w-64 {
    width: calc(var(--spacing) * 64);
  }
  .w-full {
    width: 100%;
  }
  .max-w-4xl {
    max-width: var(--container-4xl);
  }
  .max-w-7xl {
    max-width: var(--container-7xl);
  }
  .max-w-md {
    max-width: var(--container-md);
  }
  .max-w-sm {
    max-width: var(--container-sm);
  }
  .min-w-full {
    min-width: 100%;
  }
  .flex-shrink {
    flex-shrink: 1;
  }
  .flex-shrink-0 {
    flex-shrink: 0;
  }
  .border-collapse {
    border-collapse: collapse;
  }
  .origin-top-right {
    transform-origin: top right;
  }
  .-translate-x-full {
    --tw-translate-x: -100%;
    translate: var(--tw-translate-x) var(--tw-translate-y);
  }
  .-translate-y-1 {
    --tw-translate-y: calc(var(--spacing) * -1);
    translate: var(--tw-translate-x) var(--tw-translate-y);
  }
  .-translate-y-1\/2 {
    --tw-translate-y: calc(calc(1/2 * 100%) * -1);
    translate: var(--tw-translate-x) var(--tw-translate-y);
  }
  .transform {
    transform: var(--tw-rotate-x,) var(--tw-rotate-y,) var(--tw-rotate-z,) var(--tw-skew-x,) var(--tw-skew-y,);
  }
  .transform-gpu {
    transform: translateZ(0) var(--tw-rotate-x,) var(--tw-rotate-y,) var(--tw-rotate-z,) var(--tw-skew-x,) var(--tw-skew-y,);
  }
  .animate-pulse {
    animation: var(--animate-pulse);
  }
  .animate-spin {
    animation: var(--animate-spin);
  }
  .resize {
    resize: both;
  }
  .flex-wrap {
    flex-wrap: wrap;
  }
  .items-center {
    align-items: center;
  }
  .justify-between {
    justify-content: space-between;
  }
  .justify-center {
    justify-content: center;
  }
  .justify-end {
    justify-content: flex-end;
  }
  .space-y-0 {
    :where(& > :not(:last-child)) {
      --tw-space-y-reverse: 0;
      margin-block-start: calc(calc(var(--spacing) * 0) * var(--tw-space-y-reverse));
      margin-block-end: calc(calc(var(--spacing) * 0) * calc(1 - var(--tw-space-y-reverse)));
    }
  }
  .space-x-2 {
    :where(& > :not(:last-child)) {
      --tw-space-x-reverse: 0;
      margin-inline-start: calc(calc(var(--spacing) * 2) * var(--tw-space-x-reverse));
      margin-inline-end: calc(calc(var(--spacing) * 2) * calc(1 - var(--tw-space-x-reverse)));
    }
  }
  .space-x-3 {
    :where(& > :not(:last-child)) {
      --tw-space-x-reverse: 0;
      margin-inline-start: calc(calc(var(--spacing) * 3) * var(--tw-space-x-reverse));
      margin-inline-end: calc(calc(var(--spacing) * 3) * calc(1 - var(--tw-space-x-reverse)));
    }
  }
  .divide-y {
    :where(& > :not(:last-child)) {
      --tw-divide-y-reverse: 0;
      border-bottom-style: var(--tw-border-style);
      border-top-style: var(--tw-border-style);
      border-top-width: calc(1px * var(--tw-divide-y-reverse));
      border-bottom-width: calc(1px * calc(1 - var(--tw-divide-y-reverse)));
    }
  }
  .divide-gray-100 {
    :where(& > :not(:last-child)) {
      border-color: var(--color-gray-100);
    }
  }
  .divide-gray-200 {
    :where(& > :not(:last-child)) {
      border-color: var(--color-gray-200);
    }
  }
  .overflow-hidden {
    overflow: hidden;
  }
  .overflow-y-auto {
    overflow-y: auto;
  }
  .rounded {
    border-radius: 0.25rem;
  }
  .rounded-full {
    border-radius: calc(infinity * 1px);
  }
  .rounded-lg {
    border-radius: var(--radius-lg);
  }
  .rounded-md {
    border-radius: var(--radius-md);
  }
  .rounded-xl {
    border-radius: var(--radius-xl);
  }
  .border {
    border-style: var(--tw-border-style);
    border-width: 1px;
  }
  .border-2 {
    border-style: var(--tw-border-style);
    border-width: 2px;
  }
  .border-t {
    border-top-style: var(--tw-border-style);
    border-top-width: 1px;
  }
  .border-b {
    border-bottom-style: var(--tw-border-style);
    border-bottom-width: 1px;
  }
  .border-b-2 {
    border-bottom-style: var(--tw-border-style);
    border-bottom-width: 2px;
  }
  .border-black {
    border-color: var(--color-black);
  }
  .border-blue-200 {
    border-color: var(--color-blue-200);
  }
  .border-gray-100 {
    border-color: var(--color-gray-100);
  }
  .border-gray-200 {
    border-color: var(--color-gray-200);
  }
  .border-gray-300 {
    border-color: var(--color-gray-300);
  }
  .border-gray-600 {
    border-color: var(--color-gray-600);
  }
  .border-green-200 {
    border-color: var(--color-green-200);
  }
  .border-green-300 {
    border-color: var(--color-green-300);
  }
  .border-orange-200 {
    border-color: var(--color-orange-200);
  }
  .border-purple-200 {
    border-color: var(--color-purple-200);
  }
  .border-purple-600 {
    border-color: var(--color-purple-600);
  }
  .border-red-200 {
    border-color: var(--color-red-200);
  }
  .border-red-300 {
    border-color: var(--color-red-300);
  }
  .border-white {
    border-color: var(--color-white);
  }
  .border-yellow-200 {
    border-color: var(--color-yellow-200);
  }
  .bg-black {
    background-color: var(--color-black);
  }
  .bg-blue-50 {
    background-color: var(--color-blue-50);
  }
  .bg-blue-100 {
    background-color: var(--color-blue-100);
  }
  .bg-gray-50 {
    background-color: var(--color-gray-50);
  }
  .bg-gray-200 {
    background-color: var(--color-gray-200);
  }
  .bg-gray-300 {
    background-color: var(--color-gray-300);
  }
  .bg-gray-800 {
    background-color: var(--color-gray-800);
  }
  .bg-gray-900 {
    background-color: var(--color-gray-900);
  }
  .bg-green-50 {
    background-color: var(--color-green-50);
  }
  .bg-green-100 {
    background-color: var(--color-green-100);
  }
  .bg-green-600 {
    background-color: var(--color-green-600);
  }
  .bg-orange-50 {
    background-color: var(--color-orange-50);
  }
  .bg-purple-50 {
    background-color: var(--color-purple-50);
  }
  .bg-purple-100 {
    background-color: var(--color-purple-100);
  }
  .bg-purple-200 {
    background-color: var(--color-purple-200);
  }
  .bg-purple-600 {
    background-color: var(--color-purple-600);
  }
  .bg-red-50 {
    background-color: var(--color-red-50);
  }
  .bg-red-100 {
    background-color: var(--color-red-100);
  }
  .bg-red-600 {
    background-color: var(--color-red-600);
  }
  .bg-white {
    background-color: var(--color-white);
  }
  .bg-yellow-50 {
    background-color: var(--color-yellow-50);
  }
  .bg-yellow-100 {
    background-color: var(--color-yellow-100);
  }
  .bg-gradient-to-br {
    --tw-gradient-position: to bottom right in oklab;
    background-image: linear-gradient(var(--tw-gradient-stops));
  }
  .bg-gradient-to-r {
    --tw-gradient-position: to right in oklab;
    background-image: linear-gradient(var(--tw-gradient-stops));
  }
  .from-blue-600 {
    --tw-gradient-from: var(--color-blue-600);
    --tw-gradient-stops: var(--tw-gradient-via-stops, var(--tw-gradient-position), var(--tw-gradient-from) var(--tw-gradient-from-position), var(--tw-gradient-to) var(--tw-gradient-to-position));
  }
  .from-purple-500 {
    --tw-gradient-from: var(--color-purple-500);
    --tw-gradient-stops: var(--tw-gradient-via-stops, var(--tw-gradient-position), var(--tw-gradient-from) var(--tw-gradient-from-position), var(--tw-gradient-to) var(--tw-gradient-to-position));
  }
  .from-purple-600 {
    --tw-gradient-from: var(--color-purple-600);
    --tw-gradient-stops: var(--tw-gradient-via-stops, var(--tw-gradient-position), var(--tw-gradient-from) var(--tw-gradient-from-position), var(--tw-gradient-to) var(--tw-gradient-to-position));
  }
  .to-blue-600 {
    --tw-gradient-to: var(--color-blue-600);
    --tw-gradient-stops: var(--tw-gradient-via-stops, var(--tw-gradient-position), var(--tw-gradient-from) var(--tw-gradient-from-position), var(--tw-gradient-to) var(--tw-gradient-to-position));
  }
  .to-cyan-600 {
    --tw-gradient-to: var(--color-cyan-600);
    --tw-gradient-stops: var(--tw-gradient-via-stops, var(--tw-gradient-position), var(--tw-gradient-from) var(--tw-gradient-from-position), var(--tw-gradient-to) var(--tw-gradient-to-position));
  }
  .to-indigo-600 {
    --tw-gradient-to: var(--color-indigo-600);
    --tw-gradient-stops: var(--tw-gradient-via-stops, var(--tw-gradient-position), var(--tw-gradient-from) var(--tw-gradient-from-position), var(--tw-gradient-to) var(--tw-gradient-to-position));
  }
  .bg-clip-text {
    background-clip: text;
  }
  .p-4 {
    padding: calc(var(--spacing) * 4);
  }
  .p-6 {
    padding: calc(var(--spacing) * 6);
  }
  .px-2 {
    padding-inline: calc(var(--spacing) * 2);
  }
  .px-2\.5 {
    padding-inline: calc(var(--spacing) * 2.5);
  }
  .px-3 {
    padding-inline: calc(var(--spacing) * 3);
  }
  .px-4 {
    padding-inline: calc(var(--spacing) * 4);
  }
  .px-6 {
    padding-inline: calc(var(--spacing) * 6);
  }
  .px-8 {
    padding-inline: calc(var(--spacing) * 8);
  }
  .py-0 {
    padding-block: calc(var(--spacing) * 0);
  }
  .py-0\.5 {
    padding-block: calc(var(--spacing) * 0.5);
  }
  .py-1 {
    padding-block: calc(var(--spacing) * 1);
  }
  .py-1\.5 {
    padding-block: calc(var(--spacing) * 1.5);
  }
  .py-2 {
    padding-block: calc(var(--spacing) * 2);
  }
  .py-3 {
    padding-block: calc(var(--spacing) * 3);
  }
  .py-4 {
    padding-block: calc(var(--spacing) * 4);
  }
  .py-12 {
    padding-block: calc(var(--spacing) * 12);
  }
  .pl-10 {
    padding-left: calc(var(--spacing) * 10);
  }
  .text-left {
    text-align: left;
  }
  .text-2xl {
    font-size: var(--text-2xl);
    line-height: var(--tw-leading, var(--text-2xl--line-height));
  }
  .text-3xl {
    font-size: var(--text-3xl);
    line-height: var(--tw-leading, var(--text-3xl--line-height));
  }
  .text-base {
    font-size: var(--text-base);
    line-height: var(--tw-leading, var(--text-base--line-height));
  }
  .text-lg {
    font-size: var(--text-lg);
    line-height: var(--tw-leading, var(--text-lg--line-height));
  }
  .text-sm {
    font-size: var(--text-sm);
    line-height: var(--tw-leading, var(--text-sm--line-height));
  }
  .text-xl {
    font-size: var(--text-xl);
    line-height: var(--tw-leading, var(--text-xl--line-height));
  }
  .text-xs {
    font-size: var(--text-xs);
    line-height: var(--tw-leading, var(--text-xs--line-height));
  }
  .font-bold {
    --tw-font-weight: var(--font-weight-bold);
    font-weight: var(--font-weight-bold);
  }
  .font-medium {
    --tw-font-weight: var(--font-weight-medium);
    font-weight: var(--font-weight-medium);
  }
  .font-semibold {
    --tw-font-weight: var(--font-weight-semibold);
    font-weight: var(--font-weight-semibold);
  }
  .tracking-wider {
    --tw-tracking: var(--tracking-wider);
    letter-spacing: var(--tracking-wider);
  }
  .whitespace-nowrap {
    white-space: nowrap;
  }
  .text-blue-800 {
    color: var(--color-blue-800);
  }
  .text-current {
    color: currentcolor;
  }
  .text-gray-400 {
    color: var(--color-gray-400);
  }
  .text-gray-500 {
    color: var(--color-gray-500);
  }
  .text-gray-600 {
    color: var(--color-gray-600);
  }
  .text-gray-700 {
    color: var(--color-gray-700);
  }
  .text-gray-900 {
    color: var(--color-gray-900);
  }
  .text-green-800 {
    color: var(--color-green-800);
  }
  .text-purple-700 {
    color: var(--color-purple-700);
  }
  .text-red-800 {
    color: var(--color-red-800);
  }
  .text-transparent {
    color: transparent;
  }
  .text-white {
    color: var(--color-white);
  }
  .text-yellow-800 {
    color: var(--color-yellow-800);
  }
  .uppercase {
    text-transform: uppercase;
  }
  .underline {
    text-decoration-line: underline;
  }
  .placeholder-gray-400 {
    &::placeholder {
      color: var(--color-gray-400);
    }
  }
  .opacity-50 {
    opacity: 50%;
  }
  .shadow {
    --tw-shadow: 0 1px 3px 0 var(--tw-shadow-color, rgb(0 0 0 / 0.1)), 0 1px 2px -1px var(--tw-shadow-color, rgb(0 0 0 / 0.1));
    box-shadow: var(--tw-inset-shadow), var(--tw-inset-ring-shadow), var(--tw-ring-offset-shadow), var(--tw-ring-shadow), var(--tw-shadow);
  }
  .shadow-lg {
    --tw-shadow: 0 10px 15px -3px var(--tw-shadow-color, rgb(0 0 0 / 0.1)), 0 4px 6px -4px var(--tw-shadow-color, rgb(0 0 0 / 0.1));
    box-shadow: var(--tw-inset-shadow), var(--tw-inset-ring-shadow), var(--tw-ring-offset-shadow), var(--tw-ring-shadow), var(--tw-shadow);
  }
  .shadow-sm {
    --tw-shadow: 0 1px 3px 0 var(--tw-shadow-color, rgb(0 0 0 / 0.1)), 0 1px 2px -1px var(--tw-shadow-color, rgb(0 0 0 / 0.1));
    box-shadow: var(--tw-inset-shadow), var(--tw-inset-ring-shadow), var(--tw-ring-offset-shadow), var(--tw-ring-shadow), var(--tw-shadow);
  }
  .ring-1 {
    --tw-ring-shadow: var(--tw-ring-inset,) 0 0 0 calc(1px + var(--tw-ring-offset-width)) var(--tw-ring-color, currentcolor);
    box-shadow: var(--tw-inset-shadow), var(--tw-inset-ring-shadow), var(--tw-ring-offset-shadow), var(--tw-ring-shadow), var(--tw-shadow);
  }
  .ring-black {
    --tw-ring-color: var(--color-black);
  }
  .outline {
    outline-style: var(--tw-outline-style);
    outline-width: 1px;
  }
  .backdrop-blur-sm {
    --tw-backdrop-blur: blur(var(--blur-sm));
    -webkit-backdrop-filter: var(--tw-backdrop-blur,) var(--tw-backdrop-brightness,) var(--tw-backdrop-contrast,) var(--tw-backdrop-grayscale,) var(--tw-backdrop-hue-rotate,) var(--tw-backdrop-invert,) var(--tw-backdrop-opacity,) var(--tw-backdrop-saturate,) var(--tw-backdrop-sepia,);
    backdrop-filter: var(--tw-backdrop-blur,) var(--tw-backdrop-brightness,) var(--tw-backdrop-contrast,) var(--tw-backdrop-grayscale,) var(--tw-backdrop-hue-rotate,) var(--tw-backdrop-invert,) var(--tw-backdrop-opacity,) var(--tw-backdrop-saturate,) var(--tw-backdrop-sepia,);
  }
  .backdrop-filter {
    -webkit-backdrop-filter: var(--tw-backdrop-blur,) var(--tw-backdrop-brightness,) var(--tw-backdrop-contrast,) var(--tw-backdrop-grayscale,) var(--tw-backdrop-hue-rotate,) var(--tw-backdrop-invert,) var(--tw-backdrop-opacity,) var(--tw-backdrop-saturate,) var(--tw-backdrop-sepia,);
    backdrop-filter: var(--tw-backdrop-blur,) var(--tw-backdrop-brightness,) var(--tw-backdrop-contrast,) var(--tw-backdrop-grayscale,) var(--tw-backdrop-hue-rotate,) var(--tw-backdrop-invert,) var(--tw-backdrop-opacity,) var(--tw-backdrop-saturate,) var(--tw-backdrop-sepia,);
  }
  .transition-all {
    transition-property: all;
    transition-timing-function: var(--tw-ease, var(--default-transition-timing-function));
    transition-duration: var(--tw-duration, var(--default-transition-duration));
  }
  .transition-colors {
    transition-property: color, background-color, border-color, outline-color, text-decoration-color, fill, stroke, --tw-gradient-from, --tw-gradient-via, --tw-gradient-to;
    transition-timing-function: var(--tw-ease, var(--default-transition-timing-function));
    transition-duration: var(--tw-duration, var(--default-transition-duration));
  }
  .transition-shadow {
    transition-property: box-shadow;
    transition-timing-function: var(--tw-ease, var(--default-transition-timing-function));
    transition-duration: var(--tw-duration, var(--default-transition-duration));
  }
  .transition-transform {
    transition-property: transform, translate, scale, rotate;
    transition-timing-function: var(--tw-ease, var(--default-transition-timing-function));
    transition-duration: var(--tw-duration, var(--default-transition-duration));
  }
  .duration-150 {
    --tw-duration: 150ms;
    transition-duration: 150ms;
  }
  .duration-200 {
    --tw-duration: 200ms;
    transition-duration: 200ms;
  }
  .duration-300 {
    --tw-duration: 300ms;
    transition-duration: 300ms;
  }
  .ease-in-out {
    --tw-ease: var(--ease-in-out);
    transition-timing-function: var(--ease-in-out);
  }
  .ease-out {
    --tw-ease: var(--ease-out);
    transition-timing-function: var(--ease-out);
  }
  .hover\:bg-gray-50 {
    &:hover {
      @media (hover: hover) {
        background-color: var(--color-gray-50);
      }
    }
  }
  .hover\:bg-gray-100 {
    &:hover {
      @media (hover: hover) {
        background-color: var(--color-gray-100);
      }
    }
  }
  .hover\:bg-green-700 {
    &:hover {
      @media (hover: hover) {
        background-color: var(--color-green-700);
      }
    }
  }
  .hover\:bg-purple-700 {
    &:hover {
      @media (hover: hover) {
        background-color: var(--color-purple-700);
      }
    }
  }
  .hover\:bg-red-700 {
    &:hover {
      @media (hover: hover) {
        background-color: var(--color-red-700);
      }
    }
  }
  .hover\:text-gray-900 {
    &:hover {
      @media (hover: hover) {
        color: var(--color-gray-900);
      }
    }
  }
  .hover\:opacity-75 {
    &:hover {
      @media (hover: hover) {
        opacity: 75%;
      }
    }
  }
  .hover\:shadow-md {
    &:hover {
      @media (hover: hover) {
        --tw-shadow: 0 4px 6px -1px var(--tw-shadow-color, rgb(0 0 0 / 0.1)), 0 2px 4px -2px var(--tw-shadow-color, rgb(0 0 0 / 0.1));
        box-shadow: var(--tw-inset-shadow), var(--tw-inset-ring-shadow), var(--tw-ring-offset-shadow), var(--tw-ring-shadow), var(--tw-shadow);
      }
    }
  }
  .focus\:border-green-500 {
    &:focus {
      border-color: var(--color-green-500);
    }
  }
  .focus\:border-purple-500 {
    &:focus {
      border-color: var(--color-purple-500);
    }
  }
  .focus\:border-red-500 {
    &:focus {
      border-color: var(--color-red-500);
    }
  }
  .focus\:ring-2 {
    &:focus {
      --tw-ring-shadow: var(--tw-ring-inset,) 0 0 0 calc(2px + var(--tw-ring-offset-width)) var(--tw-ring-color, currentcolor);
      box-shadow: var(--tw-inset-shadow), var(--tw-inset-ring-shadow), var(--tw-ring-offset-shadow), var(--tw-ring-shadow), var(--tw-shadow);
    }
  }
  .focus\:ring-green-500 {
    &:focus {
      --tw-ring-color: var(--color-green-500);
    }
  }
  .focus\:ring-purple-500 {
    &:focus {
      --tw-ring-color: var(--color-purple-500);
    }
  }
  .focus\:ring-red-500 {
    &:focus {
      --tw-ring-color: var(--color-red-500);
    }
  }
  .focus\:ring-offset-2 {
    &:focus {
      --tw-ring-offset-width: 2px;
      --tw-ring-offset-shadow: var(--tw-ring-inset,) 0 0 0 var(--tw-ring-offset-width) var(--tw-ring-offset-color);
    }
  }
  .focus\:outline-none {
    &:focus {
      --tw-outline-style: none;
      outline-style: none;
    }
  }
  .disabled\:opacity-50 {
    &:disabled {
      opacity: 50%;
    }
  }
  .sm\:px-6 {
    @media (width >= 40rem) {
      padding-inline: calc(var(--spacing) * 6);
    }
  }
  .sm\:text-3xl {
    @media (width >= 40rem) {
      font-size: var(--text-3xl);
      line-height: var(--tw-leading, var(--text-3xl--line-height));
    }
  }
  .sm\:text-base {
    @media (width >= 40rem) {
      font-size: var(--text-base);
      line-height: var(--tw-leading, var(--text-base--line-height));
    }
  }
  .md\:h-80 {
    @media (width >= 48rem) {
      height: calc(var(--spacing) * 80);
    }
  }
  .lg\:static {
    @media (width >= 64rem) {
      position: static;
    }
  }
  .lg\:inset-0 {
    @media (width >= 64rem) {
      inset: calc(var(--spacing) * 0);
    }
  }
  .lg\:translate-x-0 {
    @media (width >= 64rem) {
      --tw-translate-x: calc(var(--spacing) * 0);
      translate: var(--tw-translate-x) var(--tw-translate-y);
    }
  }
  .lg\:px-8 {
    @media (width >= 64rem) {
      padding-inline: calc(var(--spacing) * 8);
    }
  }
}
@property --tw-translate-x {
  syntax: "*";
  inherits: false;
  initial-value: 0;
}
@property --tw-translate-y {
  syntax: "*";
  inherits: false;
  initial-value: 0;
}
@property --tw-translate-z {
  syntax: "*";
  inherits: false;
  initial-value: 0;
}
@property --tw-rotate-x {
  syntax: "*";
  inherits: false;
}
@property --tw-rotate-y {
  syntax: "*";
  inherits: false;
}
@property --tw-rotate-z {
  syntax: "*";
  inherits: false;
}
@property --tw-skew-x {
  syntax: "*";
  inherits: false;
}
@property --tw-skew-y {
  syntax: "*";
  inherits: false;
}
@property --tw-space-y-reverse {
  syntax: "*";
  inherits: false;
  initial-value: 0;
}
@property --tw-space-x-reverse {
  syntax: "*";
  inherits: false;
  initial-value: 0;
}
@property --tw-divide-y-reverse {
  syntax: "*";
  inherits: false;
  initial-value: 0;
}
@property --tw-border-style {
  syntax: "*";
  inherits: false;
  initial-value: solid;
}
@property --tw-gradient-position {
  syntax: "*";
  inherits: false;
}
@property --tw-gradient-from {
  syntax: "<color>";
  inherits: false;
  initial-value: #0000;
}
@property --tw-gradient-via {
  syntax: "<color>";
  inherits: false;
  initial-value: #0000;
}
@property --tw-gradient-to {
  syntax: "<color>";
  inherits: false;
  initial-value: #0000;
}
@property --tw-gradient-stops {
  syntax: "*";
  inherits: false;
}
@property --tw-gradient-via-stops {
  syntax: "*";
  inherits: false;
}
@property --tw-gradient-from-position {
  syntax: "<length-percentage>";
  inherits: false;
  initial-value: 0%;
}
@property --tw-gradient-via-position {
  syntax: "<length-percentage>";
  inherits: false;
  initial-value: 50%;
}
@property --tw-gradient-to-position {
  syntax: "<length-percentage>";
  inherits: false;
  initial-value: 100%;
}
@property --tw-font-weight {
  syntax: "*";
  inherits: false;
}
@property --tw-tracking {
  syntax: "*";
  inherits: false;
}
@property --tw-shadow {
  syntax: "*";
  inherits: false;
  initial-value: 0 0 #0000;
}
@property --tw-shadow-color {
  syntax: "*";
  inherits: false;
}
@property --tw-shadow-alpha {
  syntax: "<percentage>";
  inherits: false;
  initial-value: 100%;
}
@property --tw-inset-shadow {
  syntax: "*";
  inherits: false;
  initial-value: 0 0 #0000;
}
@property --tw-inset-shadow-color {
  syntax: "*";
  inherits: false;
}
@property --tw-inset-shadow-alpha {
  syntax: "<percentage>";
  inherits: false;
  initial-value: 100%;
}
@property --tw-ring-color {
  syntax: "*";
  inherits: false;
}
@property --tw-ring-shadow {
  syntax: "*";
  inherits: false;
  initial-value: 0 0 #0000;
}
@property --tw-inset-ring-color {
  syntax: "*";
  inherits: false;
}
@property --tw-inset-ring-shadow {
  syntax: "*";
  inherits: false;
  initial-value: 0 0 #0000;
}
@property --tw-ring-inset {
  syntax: "*";
  inherits: false;
}
@property --tw-ring-offset-width {
  syntax: "<length>";
  inherits: false;
  initial-value: 0px;
}
@property --tw-ring-offset-color {
  syntax: "*";
  inherits: false;
  initial-value: #fff;
}
@property --tw-ring-offset-shadow {
  syntax: "*";
  inherits: false;
  initial-value: 0 0 #0000;
}
@property --tw-outline-style {
  syntax: "*";
  inherits: false;
  initial-value: solid;
}
@property --tw-backdrop-blur {
  syntax: "*";
  inherits: false;
}
@property --tw-backdrop-brightness {
  syntax: "*";
  inherits: false;
}
@property --tw-backdrop-contrast {
  syntax: "*";
  inherits: false;
}
@property --tw-backdrop-grayscale {
  syntax: "*";
  inherits: false;
}
@property --tw-backdrop-hue-rotate {
  syntax: "*";
  inherits: false;
}
@property --tw-backdrop-invert {
  syntax: "*";
  inherits: false;
}
@property --tw-backdrop-opacity {
  syntax: "*";
  inherits: false;
}
@property --tw-backdrop-saturate {
  syntax: "*";
  inherits: false;
}
@property --tw-backdrop-sepia {
  syntax: "*";
  inherits: false;
}
@property --tw-duration {
  syntax: "*";
  inherits: false;
}
@property --tw-ease {
  syntax: "*";
  inherits: false;
}
@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}
@keyframes pulse {
  50% {
    opacity: 0.5;
  }
}
@layer properties {
  @supports ((-webkit-hyphens: none) and (not (margin-trim: inline))) or ((-moz-orient: inline) and (not (color:rgb(from red r g b)))) {
    *, ::before, ::after, ::backdrop {
      --tw-translate-x: 0;
      --tw-translate-y: 0;
      --tw-translate-z: 0;
      --tw-rotate-x: initial;
      --tw-rotate-y: initial;
      --tw-rotate-z: initial;
      --tw-skew-x: initial;
      --tw-skew-y: initial;
      --tw-space-y-reverse: 0;
      --tw-space-x-reverse: 0;
      --tw-divide-y-reverse: 0;
      --tw-border-style: solid;
      --tw-gradient-position: initial;
      --tw-gradient-from: #0000;
      --tw-gradient-via: #0000;
      --tw-gradient-to: #0000;
      --tw-gradient-stops: initial;
      --tw-gradient-via-stops: initial;
      --tw-gradient-from-position: 0%;
      --tw-gradient-via-position: 50%;
      --tw-gradient-to-position: 100%;
      --tw-font-weight: initial;
      --tw-tracking: initial;
      --tw-shadow: 0 0 #0000;
      --tw-shadow-color: initial;
      --tw-shadow-alpha: 100%;
      --tw-inset-shadow: 0 0 #0000;
      --tw-inset-shadow-color: initial;
      --tw-inset-shadow-alpha: 100%;
      --tw-ring-color: initial;
      --tw-ring-shadow: 0 0 #0000;
      --tw-inset-ring-color: initial;
      --tw-inset-ring-shadow: 0 0 #0000;
      --tw-ring-inset: initial;
      --tw-ring-offset-width: 0px;
      --tw-ring-offset-color: #fff;
      --tw-ring-offset-shadow: 0 0 #0000;
      --tw-outline-style: solid;
      --tw-backdrop-blur: initial;
      --tw-backdrop-brightness: initial;
      --tw-backdrop-contrast: initial;
      --tw-backdrop-grayscale: initial;
      --tw-backdrop-hue-rotate: initial;
      --tw-backdrop-invert: initial;
      --tw-backdrop-opacity: initial;
      --tw-backdrop-saturate: initial;
      --tw-backdrop-sepia: initial;
      --tw-duration: initial;
      --tw-ease: initial;
    }
  }
}

/* Base styles */
body {
  color: #111827;
  background-color: #f9fafb;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

h1, h2, h3, h4, h5, h6 {
  font-weight: 600;
  color: #111827;
}

/* Component classes for Hypercode */
.btn-primary {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 0.5rem 1rem;
  background-color: #9333ea;
  color: white;
  font-weight: 600;
  border-radius: 0.375rem;
  transition: all 0.2s ease-in-out;
  border: none;
  cursor: pointer;
  box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
}

.btn-primary:hover {
  background-color: #7c3aed;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
}

.btn-primary:focus {
  outline: 2px solid transparent;
  outline-offset: 2px;
  box-shadow: 0 0 0 2px #a855f7, 0 0 0 4px rgba(168, 85, 247, 0.1);
}

.btn-secondary {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 0.5rem 1rem;
  background-color: white;
  color: #374151;
  font-weight: 600;
  border: 1px solid #d1d5db;
  border-radius: 0.375rem;
  transition: all 0.2s ease-in-out;
  cursor: pointer;
  box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
}

.btn-secondary:hover {
  background-color: #f9fafb;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
}

.card {
  background-color: white;
  border-radius: 0.5rem;
  border: 1px solid #e5e7eb;
  box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
  overflow: hidden;
}

.card-elevated {
  background-color: white;
  border-radius: 0.5rem;
  border: 1px solid #e5e7eb;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
  overflow: hidden;
  transition: box-shadow 0.3s ease-in-out;
}

.card-elevated:hover {
  box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
}

.card-header {
  padding: 1.5rem;
  border-bottom: 1px solid #e5e7eb;
  background-color: #f9fafb;
}

.card-body {
  padding: 1.5rem;
}

.card-footer {
  padding: 1.5rem;
  border-top: 1px solid #f3f4f6;
  background-color: #f9fafb;
}

.nav-item {
  display: flex;
  align-items: center;
  padding: 0.5rem 0.75rem;
  font-size: 0.875rem;
  font-weight: 500;
  border-radius: 0.375rem;
  transition: colors 0.2s ease-in-out;
  text-decoration: none;
}

.nav-item-active {
  background-color: #ede9fe;
  color: #7c3aed;
}

.nav-item-inactive {
  color: #6b7280;
}

.nav-item-inactive:hover {
  color: #374151;
  background-color: #f3f4f6;
}

.header {
  background-color: white;
  box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
  border-bottom: 1px solid #e5e7eb;
}

.header-content {
  max-width: 80rem;
  margin: 0 auto;
  padding: 0 1rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  height: 4rem;
}

@media (min-width: 640px) {
  .header-content {
    padding: 0 1.5rem;
  }
}

@media (min-width: 1024px) {
  .header-content {
    padding: 0 2rem;
  }
}

.stats-card {
  background-color: white;
  border-radius: 0.5rem;
  border: 2px solid #e9d5ff;
  background-color: #faf5ff;
  padding: 1.5rem;
  box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
  transition: box-shadow 0.2s ease-in-out;
}

.stats-card:hover {
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
}

.stat-label {
  font-size: 0.875rem;
  font-weight: 500;
  color: #6b7280;
  text-transform: uppercase;
  letter-spacing: 0.025em;
}

.stat-value {
  font-size: 1.875rem;
  font-weight: 700;
  color: #111827;
  margin-top: 0.5rem;
}

.stat-change {
  font-size: 0.875rem;
  font-weight: 500;
  margin-top: 0.5rem;
}

.stat-change-positive {
  color: #059669;
}

.stat-change-negative {
  color: #dc2626;
}

.form-input {
  display: block;
  width: 100%;
  padding: 0.5rem 0.75rem;
  border: 1px solid #d1d5db;
  border-radius: 0.375rem;
  color: #111827;
  background-color: white;
  transition: colors 0.2s ease-in-out;
}

.form-input::placeholder {
  color: #9ca3af;
}

.form-input:focus {
  outline: 2px solid transparent;
  outline-offset: 2px;
  border-color: #a855f7;
  box-shadow: 0 0 0 1px #a855f7;
}

.form-select {
  display: block;
  width: 100%;
  padding: 0.5rem 0.75rem;
  border: 1px solid #d1d5db;
  border-radius: 0.375rem;
  background-color: white;
  transition: colors 0.2s ease-in-out;
}

.form-select:focus {
  outline: 2px solid transparent;
  outline-offset: 2px;
  border-color: #a855f7;
  box-shadow: 0 0 0 1px #a855f7;
}

.form-label {
  display: block;
  font-size: 0.875rem;
  font-weight: 500;
  color: #374151;
  margin-bottom: 0.25rem;
}

.form-group {
  margin-bottom: 1rem;
}

.table {
  min-width: 100%;
  border-collapse: separate;
  border-spacing: 0;
}

.table thead {
  background-color: #f9fafb;
}

.table th {
  padding: 0.75rem 1.5rem;
  text-align: left;
  font-size: 0.75rem;
  font-weight: 500;
  color: #6b7280;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  border-bottom: 1px solid #e5e7eb;
}

.table td {
  padding: 1rem 1.5rem;
  border-bottom: 1px solid #e5e7eb;
  color: #111827;
}

.table tbody tr:hover {
  background-color: #f9fafb;
}

.alert {
  border-radius: 0.375rem;
  padding: 1rem;
  margin-bottom: 1rem;
  border: 1px solid;
}

.alert-success {
  background-color: #ecfdf5;
  border-color: #bbf7d0;
  color: #166534;
}

.alert-error {
  background-color: #fef2f2;
  border-color: #fecaca;
  color: #991b1b;
}

.alert-info {
  background-color: #eff6ff;
  border-color: #bfdbfe;
  color: #1e40af;
}

.badge {
  display: inline-flex;
  align-items: center;
  padding: 0.125rem 0.625rem;
  border-radius: 9999px;
  font-size: 0.75rem;
  font-weight: 500;
}

.badge-success {
  background-color: #dcfce7;
  color: #166534;
}

.badge-error {
  background-color: #fee2e2;
  color: #991b1b;
}

.badge-info {
  background-color: #dbeafe;
  color: #1e40af;
}

.container-wide {
  max-width: 80rem;
  margin: 0 auto;
  padding: 0 1rem;
}

@media (min-width: 640px) {
  .container-wide {
    padding: 0 1.5rem;
  }
}

@media (min-width: 1024px) {
  .container-wide {
    padding: 0 2rem;
  }
}

.loading-spinner {
  animation: spin 1s linear infinite;
  border-radius: 50%;
  height: 1.5rem;
  width: 1.5rem;
  border: 2px solid transparent;
  border-bottom-color: #9333ea;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.animate-fade-in {
  animation: fadeIn 0.3s ease-out;
}

.page-transition {
  animation: fadeIn 0.3s ease-out;
}

/* Utility classes for common layouts */
.flex {
  display: flex;
}

.flex-col {
  flex-direction: column;
}

.items-center {
  align-items: center;
}

.justify-center {
  justify-content: center;
}

.justify-between {
  justify-content: space-between;
}

.space-x-1 > * + * {
  margin-left: 0.25rem;
}

.space-x-2 > * + * {
  margin-left: 0.5rem;
}

.space-x-3 > * + * {
  margin-left: 0.75rem;
}

.space-x-4 > * + * {
  margin-left: 1rem;
}

.space-y-2 > * + * {
  margin-top: 0.5rem;
}

.space-y-3 > * + * {
  margin-top: 0.75rem;
}

.space-y-4 > * + * {
  margin-top: 1rem;
}

.space-y-6 > * + * {
  margin-top: 1.5rem;
}

.space-y-8 > * + * {
  margin-top: 2rem;
}

.grid {
  display: grid;
}

.grid-cols-1 {
  grid-template-columns: repeat(1, minmax(0, 1fr));
}

.grid-cols-2 {
  grid-template-columns: repeat(2, minmax(0, 1fr));
}

.grid-cols-3 {
  grid-template-columns: repeat(3, minmax(0, 1fr));
}

.grid-cols-4 {
  grid-template-columns: repeat(4, minmax(0, 1fr));
}

.gap-4 {
  gap: 1rem;
}

.gap-6 {
  gap: 1.5rem;
}

.gap-8 {
  gap: 2rem;
}

@media (min-width: 768px) {
  .md\:grid-cols-2 {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
  
  .md\:grid-cols-3 {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }
  
  .md\:grid-cols-4 {
    grid-template-columns: repeat(4, minmax(0, 1fr));
  }
  
  .md\:flex {
    display: flex;
  }
}

@media (min-width: 1024px) {
  .lg\:grid-cols-2 {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
  
  .lg\:grid-cols-3 {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }
  
  .lg\:grid-cols-4 {
    grid-template-columns: repeat(4, minmax(0, 1fr));
  }
  
  .lg\:col-span-2 {
    grid-column: span 2 / span 2;
  }
}

/* Text utilities */
.text-xs {
  font-size: 0.75rem;
  line-height: 1rem;
}

.text-sm {
  font-size: 0.875rem;
  line-height: 1.25rem;
}

.text-base {
  font-size: 1rem;
  line-height: 1.5rem;
}

.text-lg {
  font-size: 1.125rem;
  line-height: 1.75rem;
}

.text-xl {
  font-size: 1.25rem;
  line-height: 1.75rem;
}

.text-2xl {
  font-size: 1.5rem;
  line-height: 2rem;
}

.text-3xl {
  font-size: 1.875rem;
  line-height: 2.25rem;
}

.font-medium {
  font-weight: 500;
}

.font-semibold {
  font-weight: 600;
}

.font-bold {
  font-weight: 700;
}

/* Color utilities */
.text-gray-500 {
  color: #6b7280;
}

.text-gray-600 {
  color: #4b5563;
}

.text-gray-700 {
  color: #374151;
}

.text-gray-900 {
  color: #111827;
}

.text-purple-600 {
  color: #9333ea;
}

.text-purple-700 {
  color: #7c3aed;
}

.text-white {
  color: white;
}

/* Background utilities */
.bg-white {
  background-color: white;
}

.bg-gray-50 {
  background-color: #f9fafb;
}

.bg-gray-100 {
  background-color: #f3f4f6;
}

.bg-purple-50 {
  background-color: #faf5ff;
}

.bg-purple-100 {
  background-color: #f3e8ff;
}

.bg-purple-600 {
  background-color: #9333ea;
}

/* Margin and padding utilities */
.m-0 {
  margin: 0;
}

.mt-1 {
  margin-top: 0.25rem;
}

.mt-2 {
  margin-top: 0.5rem;
}

.mt-4 {
  margin-top: 1rem;
}

.mt-6 {
  margin-top: 1.5rem;
}

.mt-8 {
  margin-top: 2rem;
}

.mb-2 {
  margin-bottom: 0.5rem;
}

.mb-4 {
  margin-bottom: 1rem;
}

.mb-6 {
  margin-bottom: 1.5rem;
}

.mb-8 {
  margin-bottom: 2rem;
}

.p-4 {
  padding: 1rem;
}

.p-6 {
  padding: 1.5rem;
}

.px-3 {
  padding-left: 0.75rem;
  padding-right: 0.75rem;
}

.px-4 {
  padding-left: 1rem;
  padding-right: 1rem;
}

.px-6 {
  padding-left: 1.5rem;
  padding-right: 1.5rem;
}

.py-2 {
  padding-top: 0.5rem;
  padding-bottom: 0.5rem;
}

.py-4 {
  padding-top: 1rem;
  padding-bottom: 1rem;
}

.py-8 {
  padding-top: 2rem;
  padding-bottom: 2rem;
}

/* Border utilities */
.border {
  border-width: 1px;
}

.border-gray-200 {
  border-color: #e5e7eb;
}

.border-gray-300 {
  border-color: #d1d5db;
}

.rounded-md {
  border-radius: 0.375rem;
}

.rounded-lg {
  border-radius: 0.5rem;
}

/* Responsive utilities */
.hidden {
  display: none;
}

@media (min-width: 640px) {
  .sm\:block {
    display: block;
  }
  
  .sm\:flex {
    display: flex;
  }
  
  .sm\:px-6 {
    padding-left: 1.5rem;
    padding-right: 1.5rem;
  }
  
  .sm\:text-3xl {
    font-size: 1.875rem;
    line-height: 2.25rem;
  }
}

@media (min-width: 768px) {
  .md\:block {
    display: block;
  }
  
  .md\:flex {
    display: flex;
  }
}

@media (min-width: 1024px) {
  .lg\:px-8 {
    padding-left: 2rem;
    padding-right: 2rem;
  }
  
  .lg\:text-4xl {
    font-size: 2.25rem;
    line-height: 2.5rem;
  }
}

/* Accessibility */
.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border: 0;
}

.focus\:not-sr-only:focus {
  position: static;
  width: auto;
  height: auto;
  padding: inherit;
  margin: inherit;
  overflow: visible;
  clip: auto;
  white-space: normal;
}
        """
        css_output = self.output_dir / "styles.css"
        
        # write the input CSS to a temporary file
        with open(css_output, 'w', encoding='utf-8') as f:
            f.write(css_input)
        print("🔧 Building Tailwind CSS...")

        return False

    def _analyze_components(self):
        """Analyze registered components"""
        try:
            from .decorators import _registry
            self.components = _registry.get_all_components()
            self.state_classes = _registry.get_all_state_classes()
        except ImportError:
            print("⚠️ Could not import component registry")
            self.components = {}
            self.state_classes = {}
        
        print(f"📊 Found {len(self.components)} components")
        print(f"📊 Found {len(self.state_classes)} state classes")

    def _generate_html(self, app_title: str):
        """Generate main HTML file with proper element IDs"""
        
        # Get CSS link
        css_link = self._get_css_link()
        
        html_content = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{app_title}</title>
    
    {css_link}
    
    <!-- Fonts -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@100;200;300;400;500;600;700;800;900&display=swap" rel="stylesheet">
    
    <!-- Meta tags -->
    <meta name="description" content="{app_title} - Built with YoGuido Framework">
    <meta name="theme-color" content="#7c3aed">
    
    <!-- Favicon -->
    <link rel="icon" type="image/svg+xml" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>🔧</text></svg>">
    
    <style>
        /* Base styles before CSS loads */
        body {{
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            margin: 0;
            padding: 0;
            background-color: #f9fafb;
            color: #111827;
            line-height: 1.5;
        }}
        
        /* Loading animation */
        @keyframes pulse {{
            0%, 100% {{ opacity: 1; }}
            50% {{ opacity: 0.5; }}
        }}
        
        @keyframes spin {{
            0% {{ transform: rotate(0deg); }}
            100% {{ transform: rotate(360deg); }}
        }}
        
        .loading-animation {{
            animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
        }}
        
        /* Loading screen styles */
        .loading-screen {{
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background-color: #f9fafb;
            display: flex;
            align-items: center;
            justify-content: center;
            z-index: 50;
        }}
        
        .loading-content {{
            text-align: center;
            max-width: 400px;
            padding: 2rem;
        }}
        
        .spinner {{
            width: 3rem;
            height: 3rem;
            border: 4px solid #e5e7eb;
            border-top: 4px solid #7c3aed;
            border-radius: 50%;
            margin: 0 auto 1rem;
            animation: spin 1s linear infinite;
        }}
        
        .loading-title {{
            font-size: 1.25rem;
            font-weight: 600;
            color: #111827;
            margin: 0 0 0.5rem 0;
        }}
        
        .loading-subtitle {{
            color: #6b7280;
            margin: 0 0 1rem 0;
        }}
        
        .loading-status {{
            font-size: 0.875rem;
            color: #6b7280;
            margin-top: 1rem;
        }}
        
        /* App content */
        .app-content {{
            min-height: 100vh;
            display: none;
        }}
        
        /* State management */
        .yoguido-loading .app-content {{
            display: none;
        }}
        
        .yoguido-loaded .loading-screen {{
            display: none;
        }}
        
        .yoguido-loaded .app-content {{
            display: block;
        }}
        
        /* Error display */
        .error-display {{
            position: fixed;
            top: 1rem;
            right: 1rem;
            z-index: 50;
            max-width: 28rem;
        }}
        
        .error-content {{
            background-color: #fef2f2;
            border: 1px solid #fecaca;
            color: #991b1b;
            border-radius: 0.5rem;
            padding: 1rem;
            box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
            display: flex;
            align-items: flex-start;
        }}
        
        .error-icon {{
            flex-shrink: 0;
            margin-right: 0.75rem;
        }}
        
        .error-text {{
            flex: 1;
            min-width: 0;
        }}
        
        .error-title {{
            font-weight: 500;
            margin: 0 0 0.25rem 0;
        }}
        
        .error-message {{
            font-size: 0.875rem;
            margin: 0;
        }}
        
        .error-close {{
            background: none;
            border: none;
            color: currentColor;
            opacity: 0.5;
            cursor: pointer;
            padding: 0;
            margin-left: 1rem;
        }}
        
        .error-close:hover {{
            opacity: 0.75;
        }}
        
        /* Utilities */
        .hidden {{
            display: none !important;
        }}
        
        .sr-only {{
            position: absolute;
            width: 1px;
            height: 1px;
            padding: 0;
            margin: -1px;
            overflow: hidden;
            clip: rect(0, 0, 0, 0);
            white-space: nowrap;
            border: 0;
        }}
    </style>
</head>

<body class="yoguido-loading">
    <!-- Skip to main content -->
    <a href="#app-content" class="sr-only">Skip to main content</a>
    
    <!-- Main application container -->
    <div id="yoguido-app">
        
        <!-- Loading screen -->
        <div id="loading" class="loading-screen">
            <div class="loading-content">
                <div class="loading-animation">
                    <div class="spinner"></div>
                </div>
                <h2 class="loading-title">Loading {app_title}</h2>
                <p class="loading-subtitle">Powered by YoGuido Framework</p>
                <div class="loading-status">
                    {'✅ Using local Tailwind CSS' if self.css_built else '⚠️ Using fallback CSS'}
                </div>
            </div>
        </div>
        
        <!-- Main app content with correct ID -->
        <div id="app-content" class="app-content">
            <!-- Components will be rendered here by JavaScript -->
        </div>
        
        <!-- Error display -->
        <div id="error-display" class="error-display hidden">
            <div class="error-content">
                <div class="error-icon">
                    <svg width="20" height="20" fill="currentColor" viewBox="0 0 20 20">
                        <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clip-rule="evenodd"/>
                    </svg>
                </div>
                <div class="error-text">
                    <h4 class="error-title">Application Error</h4>
                    <p id="error-message" class="error-message"></p>
                </div>
                <button id="close-error" class="error-close">
                    <svg width="16" height="16" fill="currentColor" viewBox="0 0 20 20">
                        <path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd"/>
                    </svg>
                </button>
            </div>
        </div>
        
        <!-- Notification container -->
        <div id="notification-container"></div>
        
        <!-- Accessibility live region -->
        <div aria-live="polite" aria-atomic="true" class="sr-only" id="live-region"></div>
    </div>
    
    <!-- JavaScript application -->
    <script src="main.js"></script>
    
    <!-- Initialize app -->
    <script>
        document.addEventListener('DOMContentLoaded', function() {{
            // Mark app as loaded
            document.body.classList.remove('yoguido-loading');
            document.body.classList.add('yoguido-loaded');
            
            // Setup error close handler
            const closeErrorBtn = document.getElementById('close-error');
            const errorDisplay = document.getElementById('error-display');
            
            if (closeErrorBtn && errorDisplay) {{
                closeErrorBtn.addEventListener('click', function() {{
                    errorDisplay.classList.add('hidden');
                }});
            }}
            
            console.log('🎉 YoGuido app initialized successfully!');
            console.log('📊 CSS Method: {("Local Tailwind" if self.css_built else "Fallback")}');
        }});
        
        // Global error handler
        window.addEventListener('error', function(event) {{
            console.error('Global error:', event.error);
            
            const errorDisplay = document.getElementById('error-display');
            const errorMessage = document.getElementById('error-message');
            
            if (errorDisplay && errorMessage) {{
                errorMessage.textContent = event.error.message || 'An unexpected error occurred';
                errorDisplay.classList.remove('hidden');
            }}
        }});
        
        // Unhandled promise rejection handler
        window.addEventListener('unhandledrejection', function(event) {{
            console.error('Unhandled promise rejection:', event.reason);
        }});
    </script>
</body>
</html>'''
        
        # Write HTML file
        with open(self.output_dir / "index.html", 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print("📄 Generated index.html with proper element IDs")

    def _get_css_link(self) -> str:
        """Get the appropriate CSS link (local or CDN fallback)"""
        css_file = self.output_dir / "styles.css"
        
        if css_file.exists() and self.css_built:
            return '''<!-- Local Tailwind CSS -->
    <link rel="stylesheet" href="styles.css">'''
        else:
            return '''<!-- Tailwind CSS CDN Fallback -->
    <script src="https://cdn.tailwindcss.com"></script>
    <script>
        tailwind.config = {{
            theme: {{
                extend: {{
                    colors: {{
                        purple: {{
                            50: '#faf5ff', 100: '#f3e8ff', 200: '#e9d5ff',
                            300: '#d8b4fe', 400: '#c084fc', 500: '#a855f7',
                            600: '#9333ea', 700: '#7c3aed', 800: '#6b21a8', 900: '#581c87'
                        }}
                    }}
                }}
            }}
        }}
    </script>'''

    def _generate_javascript(self):
        """Generate the main JavaScript file with FIXED button event handling"""
        
        js_content = '''// FIXED YoGuido JavaScript Runtime with Working Button Events
console.log("🚀 YoGuido JavaScript is loading...");

class YoGuidoApp {
    constructor() {
        console.log("🏗️ YoGuidoApp constructor called");
        this.state = {};
        this.eventHandlers = {};
        this.componentTree = [];
        this.buttonHandlers = new Map();
    }
    
    async init() {
        console.log("🎬 YoGuidoApp.init() called");
        
        // Hide loading, show app
        const loading = document.getElementById('loading');
        const appContent = document.getElementById('app-content');
        
        if (loading) {
            loading.style.display = 'none';
            console.log("✅ Hidden loading div");
        }
        
        if (appContent) {
            appContent.style.display = 'block';
            console.log("✅ Showed app content div");
        } else {
            console.log("❌ Could not find app-content div");
            return;
        }
        
        // Initial render
        console.log("🎨 Calling initial render...");
        await this.render();
    }
    
    async render() {
        try {
            console.log("🎨 Starting render...");
            
            const response = await fetch('/api/render', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' }
            });
            
            console.log("📡 /api/render response status:", response.status);
            
            if (!response.ok) {
                throw new Error(`Render failed: ${response.statusText}`);
            }
            
            const data = await response.json();
            console.log("📊 Render response data:", data);
            
            this.componentTree = data.component_tree || [];
            console.log("🌳 Component tree:", this.componentTree);
            
            this.renderComponentTree();
            
        } catch (error) {
            console.error("❌ Render error:", error);
            this.showError(error.message);
        }
    }
    
    renderComponentTree() {
        console.log("🖼️ Rendering component tree with", this.componentTree.length, "components");
        
        const container = document.getElementById('app-content');
        if (!container) {
            console.error("❌ Could not find app-content container!");
            return;
        }
        
        // Clear container
        container.innerHTML = '';
        
        // Clear existing button handlers
        this.buttonHandlers.clear();
        
        // Render each component
        this.componentTree.forEach((component, index) => {
            console.log(`🧩 Rendering component ${index}: ${component.type}`);
            try {
                const element = this.createElement(component);
                container.appendChild(element);
            } catch (error) {
                console.error(`❌ Failed to render component ${index}:`, error);
            }
        });
        
        console.log("✅ Component tree rendering complete");
        console.log(`🎯 Registered ${this.buttonHandlers.size} button handlers`);
    }
    
    createElement(componentData) {
        const { type, id, props, handlers } = componentData;
        
        switch (type) {
            case 'title':
                return this.createTitle(id, props);
            case 'text':
                return this.createText(id, props);
            case 'button':
                return this.createButton(id, props, handlers);
            case 'container':
                return this.createContainer(id, props, componentData.children || []);
            case 'input_text':
                return this.createInputText(id, props);
            case 'select':
                return this.createSelect(id, props);
            case 'checkbox':
                return this.createCheckbox(id, props);
            case 'table':
                return this.createTable(id, props);
            default:
                console.warn(`Unknown component type: ${type}`);
                const div = document.createElement('div');
                div.textContent = `Unknown component: ${type}`;
                return div;
        }
    }
    
    createTitle(id, props) {
        const level = props.level || 1;
        const element = document.createElement(`h${level}`);
        element.id = id;
        element.textContent = props.text || '';
        element.className = props.class_name || 'text-2xl font-bold text-gray-900 mb-4';
        return element;
    }
    
    createText(id, props) {
        const element = document.createElement('p');
        element.id = id;
        element.textContent = props.content || '';
        element.className = props.class_name || 'text-gray-600 mb-2';
        return element;
    }
    
    createButton(id, props, handlers) {
        console.log(`🔘 Creating button: ${id}`, props, handlers);
        
        const element = document.createElement('button');
        element.id = id;
        element.textContent = props.label || 'Button';
        element.className = props.class_name || 'bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600 transition-colors';
        
        // CRITICAL FIX: Add click handler if it exists
        if (handlers && handlers.click) {
            const handlerId = handlers.click;
            console.log(`🎯 Registering click handler for button ${id}: ${handlerId}`);
            
            // Store handler reference
            this.buttonHandlers.set(id, handlerId);
            
            // Add click event listener
            element.addEventListener('click', async (event) => {
                console.log(`🔥 Button clicked: ${id} -> ${handlerId}`);
                event.preventDefault();
                
                try {
                    // Send event to backend
                    await this.sendButtonClick(id, handlerId);
                } catch (error) {
                    console.error(`❌ Button click failed for ${id}:`, error);
                }
            });
            
            console.log(`✅ Click handler registered for button ${id}`);
        } else {
            console.log(`⚠️ No click handler for button ${id}`);
        }
        
        return element;
    }
    
    async sendButtonClick(buttonId, handlerId) {
        console.log(`📡 Sending button click: ${buttonId} -> ${handlerId}`);
        
        try {
            const response = await fetch('/hcc', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    event_type: 'click',
                    element_id: buttonId,
                    handler_id: handlerId,
                    timestamp: new Date().toISOString()
                })
            });
            
            console.log(`📡 Button click response status: ${response.status}`);
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            const data = await response.json();
            console.log(`📊 Button click response:`, data);
            
            // If server returns updated component tree, re-render
            if (data.component_tree) {
                console.log("🔄 Re-rendering after button click...");
                this.componentTree = data.component_tree;
                this.renderComponentTree();
            }
            
            // Show any alerts or notifications
            if (data.status === 'success') {
                console.log("✅ Button click processed successfully");
            }
            
        } catch (error) {
            console.error(`❌ Failed to send button click:`, error);
            this.showError(`Button click failed: ${error.message}`);
        }
    }
    
    createContainer(id, props, children) {
        const element = document.createElement('div');
        element.id = id;
        element.className = props.class_name || 'p-6';
        
        children.forEach(child => {
            element.appendChild(this.createElement(child));
        });
        
        return element;
    }
    
    createInputText(id, props) {
        const element = document.createElement('input');
        element.type = 'text';
        element.id = id;
        element.placeholder = props.placeholder || '';
        element.value = props.value || '';
        element.className = props.class_name || 'border border-gray-300 rounded px-3 py-2';
        
        // Add input change handler
        element.addEventListener('input', async (event) => {
            await this.sendInputChange(id, event.target.value);
        });
        
        return element;
    }
    
    async sendInputChange(inputId, value) {
        try {
            const response = await fetch('/hcc', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    event_type: 'input',
                    element_id: inputId,
                    value: value,
                    timestamp: new Date().toISOString()
                })
            });
            
            if (response.ok) {
                const data = await response.json();
                console.log(`📝 Input change processed:`, data);
            }
        } catch (error) {
            console.error(`❌ Failed to send input change:`, error);
        }
    }
    
    createSelect(id, props) {
        const element = document.createElement('select');
        element.id = id;
        element.className = props.class_name || 'border border-gray-300 rounded px-3 py-2';
        
        (props.options || []).forEach(option => {
            const optionElement = document.createElement('option');
            optionElement.value = option.value || option;
            optionElement.textContent = option.label || option;
            if (props.value === optionElement.value) {
                optionElement.selected = true;
            }
            element.appendChild(optionElement);
        });
        
        // Add change handler
        element.addEventListener('change', async (event) => {
            await this.sendInputChange(id, event.target.value);
        });
        
        return element;
    }
    
    createCheckbox(id, props) {
        const wrapper = document.createElement('div');
        wrapper.className = props.class_name || 'flex items-center space-x-2';
        
        const element = document.createElement('input');
        element.type = 'checkbox';
        element.id = id;
        element.checked = props.checked || false;
        element.className = 'rounded';
        
        const label = document.createElement('label');
        label.htmlFor = id;
        label.textContent = props.label || '';
        label.className = 'text-sm font-medium text-gray-700';
        
        wrapper.appendChild(element);
        wrapper.appendChild(label);
        
        // Add change handler
        element.addEventListener('change', async (event) => {
            await this.sendInputChange(id, event.target.checked);
        });
        
        return wrapper;
    }
    
    createTable(id, props) {
        const wrapper = document.createElement('div');
        wrapper.className = 'overflow-x-auto';
        
        const table = document.createElement('table');
        table.id = id;
        table.className = props.class_name || 'w-full divide-y divide-gray-200';
        
        // Create header
        if (props.columns && props.columns.length > 0) {
            const thead = document.createElement('thead');
            thead.className = 'bg-gray-50';
            
            const headerRow = document.createElement('tr');
            props.columns.forEach(column => {
                const th = document.createElement('th');
                th.textContent = column.charAt(0).toUpperCase() + column.slice(1);
                th.className = 'px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider';
                headerRow.appendChild(th);
            });
            
            thead.appendChild(headerRow);
            table.appendChild(thead);
        }
        
        // Create body
        const tbody = document.createElement('tbody');
        tbody.className = 'bg-white divide-y divide-gray-200';
        
        (props.data || []).forEach((row, rowIndex) => {
            const tr = document.createElement('tr');
            tr.className = rowIndex % 2 === 0 ? 'bg-white' : 'bg-gray-50';
            
            (props.columns || Object.keys(row)).forEach(column => {
                const td = document.createElement('td');
                td.textContent = row[column] || '';
                td.className = 'px-6 py-4 whitespace-nowrap text-sm text-gray-900';
                tr.appendChild(td);
            });
            
            tbody.appendChild(tr);
        });
        
        table.appendChild(tbody);
        wrapper.appendChild(table);
        
        return wrapper;
    }
    
    showError(message) {
        console.error("🚨 Showing error:", message);
        const errorDisplay = document.getElementById('error-display');
        const errorMessage = document.getElementById('error-message');
        
        if (errorDisplay && errorMessage) {
            errorMessage.textContent = message;
            errorDisplay.classList.remove('hidden');
        }
    }
    
    // Debug method to inspect current state
    debugState() {
        console.log("🔍 DEBUG STATE:");
        console.log("   Component tree:", this.componentTree);
        console.log("   Button handlers:", this.buttonHandlers);
        console.log("   State:", this.state);
    }
}

// Initialize app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    console.log("📄 DOM loaded, initializing YoGuido app...");
    const app = new YoGuidoApp();
    app.init();
    
    // Make app globally available for debugging
    window.yoguidoApp = app;
    console.log("🌍 App available globally as window.yoguidoApp");
    
    // Add debug helper
    window.debugYoGuido = () => {
        app.debugState();
    };
    console.log("🔍 Debug helper available as window.debugYoGuido()");
});

console.log("✅ YoGuido JavaScript loaded successfully");'''
        
        with open(self.output_dir / "main.js", 'w', encoding='utf-8') as f:
            f.write(js_content)
        
        print("📄 Generated main.js with FIXED button event handling")