# Kaggle release steps

1. Run `make all` (or the five scripts) and check that `validate_dataset.py` prints PASS.
2. On Kaggle: Create > New Dataset. Drag in every file from `kaggle/1-upload-these/`.
3. Title and subtitle: copy from `kaggle/2-helpers/KAGGLE_FIELDS.md`. Set the URL to
   `pakistan-punjab-groundwater-levels`.
4. Create, then on the dataset page: add the cover image `kaggle/2-helpers/cover_1280x640.png`, paste the description,
   choose the licence "Other (specified in description)" and the tags from `KAGGLE_FIELDS.md`.
5. In the description, replace `[YEAR]` in the NERC acknowledgement with the year shown on the BGS catalogue page
   for the dataset.
6. Code > New Notebook on the dataset page, File > Import notebook, choose
   `kaggle/2-helpers/starter_notebook.ipynb`, run all, then Save Version.
