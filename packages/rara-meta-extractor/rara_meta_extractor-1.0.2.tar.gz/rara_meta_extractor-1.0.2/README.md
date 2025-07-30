# RaRa Meta Extractor

![Py3.10](https://img.shields.io/badge/python-3.10-green.svg)
![Py3.11](https://img.shields.io/badge/python-3.11-green.svg)
![Py3.12](https://img.shields.io/badge/python-3.12-green.svg)

**`rara-meta-extractor`** is a  Python library for extracting relevant meta information for cataloging.


---

## ✨ Features  

- Coming soon
---


## ⚡ Quick Start  

Get started with `rara-meta-extractor` in just a few steps:

1. **Install the Package**  
   Ensure you"re using Python 3.10 or above, then run:  
   ```bash
   pip install rara-meta-extractor
   ```

2. **Import and Use**  
   Example usage to link entries with default configuration:  

   ```python
    from rara_meta_extractor.llama_extractor import LlamaExtractor
    from pprint import pprint

    text = """
       JUMALAL EI OLE AEGA

       Toimetanud Milvi Teesalu
       Kaane kujundanud Piret Tuur
       Autoriõigus: Marje Ernits ja OÜ Eesti Raamat, 2019
       ISBN 978-9949-683-96-3
       ISBN 978-9949-683-97-0 (epub)
    """

    fields = [
      "editor", "designer", "isbn", "author",
      "copyright year", "title"
    ]

    llama_extractor = LlamaExtractor(
        llama_host_url="http://local-llama:8080",
        fields=fields,
        temperature=0.3
    )

    extracted_info = llama_extractor.extract(text)
    pprint(extracted_info)
   ```
   **Out:**

   ```
   {
     "editor": ["Milvi Teesalu"],
     "designer": ["Piret Tuur"],
     "isbn": ["978-9949-683-96-3", "978-9949-683-97-0"],
     "author": ["Marje Ernits ja OÜ Eesti Raamat"],
     "copyright year": ["2019"],
     "title": ["JUMALAL EI OLE AEGA"]
   }
   ```

---



## ⚙️ Installation Guide

Follow the steps below to install the `rara-meta-extractor` package, either via `pip` or locally.

---

### Installation via `pip`

<details><summary>Click to expand</summary>

1. **Set Up Your Python Environment**  
   Create or activate a Python environment using Python **3.10** or above.

2. **Install the Package**  
   Run the following command:  
   ```bash
   pip install rara-meta-extractor
   ```
</details>

---

### Local Installation

Follow these steps to install the `rara-meta-extractor` package locally:  

<details><summary>Click to expand</summary>


1. **Clone the Repository**  
   Clone the repository and navigate into it:  
   ```bash
   git clone <repository-url>
   cd <repository-directory>
   ```

2. **Set Up Python Environment**  
   Create or activate a Python environment using Python 3.10 or above. E.g:
   ```bash
   conda create -n py310 python==3.10
   conda activate py310
   ```

3. **Install Build Package**  
   Install the `build` package to enable local builds:  
   ```bash
   pip install build
   ```

4. **Build the Package**  
   Run the following command inside the repository:  
   ```bash
   python -m build
   ```

5. **Install the Package**  
   Install the built package locally:  
   ```bash
   pip install .
   ```

</details>

---

## 🚀 Testing Guide

Follow these steps to test the `rara-meta-extractor` package.


### How to Test

<details><summary>Click to expand</summary>

1. **Clone the Repository**  
   Clone the repository and navigate into it:  
   ```bash
   git clone <repository-url>
   cd <repository-directory>
   ```

2. **Set Up Python Environment**  
   Create or activate a Python environment using Python 3.10 or above.

3. **Install Build Package**  
   Install the `build` package:  
   ```bash
   pip install build
   ```

4. **Build the Package**  
   Build the package inside the repository:  
   ```bash
   python -m build
   ```

5. **Install with Testing Dependencies**  
   Install the package along with its testing dependencies:  
   ```bash
   pip install .[testing]
   ```

6. **Run Tests**  
   Run the test suite from the repository root:  
   ```bash
   python -m pytest -v tests
   ```

---

</details>


## 📝 Documentation

Coming soon


## 🔍 Usage Examples

Coming soon
