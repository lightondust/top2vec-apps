a streamlit app for top2vec 

- about top2vec: https://github.com/ddangelov/Top2Vec
- [demo site](https://www.wisdparad.com/top2vec/)

# how to

- run sample page

download model and font data from 
https://graph-pub.s3.ap-northeast-1.amazonaws.com/top2vec/data.zip
extract it to `top2vec-apps`

```
cd app
streamlit run app.py
```

### use your own model

- put model file under 'data/model'
- implement a model class in `app_model.py` and add it to `model_class_map`
- if the model is not English and you need a tokenizer, just implement a tokenizer and set it to the model
  - examples in `app_data.py`(`LivedoorModel`, `ChOtModel` etc.)

