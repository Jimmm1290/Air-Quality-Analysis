# Air Quality Analysis

![Kota terpapar polusi udara](image.png)

- By: **_Jim Jauhary Muhammad_**
- Username: **_mijim_aja_**

## Section 1: Repository

1. **Data**: Folder yang berisi datataset mentah yang digunakan sebagai acuan analisis. Dataset berkaitan dengan data kualitas udara yang ada di setiap stasiun di China.
2. **Dashboard**: Isi folder ini terdiri dari dua file, yaitu file `dashboard.py` dan `main-data.csv`. File `dashboard.py` merupakan file yang berisi code pembangunan dashboard sedangkan `main-data.csv` merupakan data siap pakai yang digunakan dalam pembuatan dashboard.
3. **notebook.ipynb**: File yang berisi dokumentasi penulis dalam melakukan Data Wrangling dan Exploratory Data Analysis menggunakan Python.
4. **requirements.txt**: Merupakan file txt yang berisi library-library yang dibutuhkan dala project analisis kali ini. `requirements.txt` akan digunakan saat membuat environtment anaconda.

## Section 2: Setup Environment

```
conda create --prefix ./env python=3.11.5
conda activate ./env
pip install -r requirements.txt
```

**Note:** Prefix disini berarti menggunakan directory path sebagai nama environment. Oleh karena itu, disarankan untuk masuk terlebih dahulu ke directory project di anaconda prompt lalu menjalankan aktivasi environtment.

## Section 3: Run Streamlit App

```
streamlit run dashboard.py
```
