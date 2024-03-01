from tensorflow.keras.models import load_model
import pickle

model = load_model("saved_models\lstm_saved_model.h5")

# load the tokenizer
with open('saved_tokenizer/tokenizer.pkl', 'rb') as tokenizer_file:
    tokenizer = pickle.load(tokenizer_file)    



