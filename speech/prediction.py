import numpy as np
import librosa
from tensorflow.keras.models import model_from_json
import pickle

# Step 1: Load the model
json_file = open('model_files/CNN_model.json', 'r')
loaded_model_json = json_file.read()
json_file.close()
loaded_model = model_from_json(loaded_model_json)

# Load weights into the model
loaded_model.load_weights('model_files/best_model1_weights.h5')
print("Loaded model from disk")

# Step 2: Load the scaler and encoder
with open('model_files/scaler2.pickle', 'rb') as f:
    scaler2 = pickle.load(f)

with open('model_files/encoder2.pickle', 'rb') as f:
    encoder2 = pickle.load(f)

print("Scaler and encoder loaded successfully")

# Step 3: Define the feature extraction functions
def zcr(data, frame_length, hop_length):
    return np.squeeze(librosa.feature.zero_crossing_rate(data, frame_length=frame_length, hop_length=hop_length))

def rmse(data, frame_length=2048, hop_length=512):
    return np.squeeze(librosa.feature.rms(data, frame_length=frame_length, hop_length=hop_length))

def mfcc(data, sr, frame_length=2048, hop_length=512, flatten=True):
    mfccs = librosa.feature.mfcc(data, sr=sr)
    return np.squeeze(mfccs.T) if not flatten else np.ravel(mfccs.T)

def extract_features(data, sr=22050, frame_length=2048, hop_length=512):
    result = np.array([])
    
    # Extract features
    zcr_feat = zcr(data, frame_length, hop_length)
    rmse_feat = rmse(data, frame_length, hop_length)
    mfcc_feat = mfcc(data, sr, frame_length, hop_length)
    
    # Pad features to ensure consistent length
    max_length = 2376  # Total number of features expected
    
    # Concatenate all features
    result = np.concatenate((zcr_feat, rmse_feat, mfcc_feat))
    
    # Pad with zeros if shorter than expected
    if result.shape[0] < max_length:
        result = np.pad(result, (0, max_length - result.shape[0]))
    # Truncate if longer than expected
    else:
        result = result[:max_length]
        
    return result

def get_predict_feat(path):
    d, s_rate = librosa.load(path, duration=2.5, offset=0.6)  # Load a specific duration of the audio
    res = extract_features(d)
    result = np.array(res)
    result = np.reshape(result, newshape=(1, 2376))  # Ensure the correct shape for the input
    i_result = scaler2.transform(result)  # Scale the features
    final_result = np.expand_dims(i_result, axis=2)  # Add batch dimension
    return final_result

# Step 4: Make predictions
emotions1 = {1: 'Neutral', 2: 'Calm', 3: 'Happy', 4: 'Sad', 5: 'Angry', 6: 'Fear', 7: 'Disgust', 8: 'Surprise'}

def prediction(path1):
    res = get_predict_feat(path1)
    predictions = loaded_model.predict(res)
    y_pred = encoder2.inverse_transform(predictions)
    return y_pred[0][0]  # Return the emotion string directly