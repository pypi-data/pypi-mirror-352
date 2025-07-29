
from fastapi import FastAPI
import os
import numpy as np
import pandas as pd
import gencrafter as why
from datetime import datetime, timezone
from pyAudioAnalysis import audioBasicIO as aIO
from pyAudioAnalysis import MidTermFeatures as aF
import logging
from typing import Dict, Any, List, Tuple

app = FastAPI()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
AUDIO_DIR = "./recordings"
SUPPORTED_FORMATS = ('.wav', '.mp3', '.ogg', '.flac')


def get_feature_names() -> List[str]:
    """Returns the standard 68 mid-term feature names"""
    return [
        'zcr_mean', 'energy_mean', 'energy_entropy_mean', 'spectral_centroid_mean',
        'spectral_spread_mean', 'spectral_entropy_mean', 'spectral_flux_mean',
        'spectral_rolloff_mean', 'mfcc_1_mean', 'mfcc_2_mean', 'mfcc_3_mean',
        'mfcc_4_mean', 'mfcc_5_mean', 'mfcc_6_mean', 'mfcc_7_mean', 'mfcc_8_mean',
        'mfcc_9_mean', 'mfcc_10_mean', 'mfcc_11_mean', 'mfcc_12_mean', 'mfcc_13_mean',
        'chroma_1_mean', 'chroma_2_mean', 'chroma_3_mean', 'chroma_4_mean',
        'chroma_5_mean', 'chroma_6_mean', 'chroma_7_mean', 'chroma_8_mean',
        'chroma_9_mean', 'chroma_10_mean', 'chroma_11_mean', 'chroma_12_mean',
        'chroma_std', 'zcr_std', 'energy_std', 'energy_entropy_std',
        'spectral_centroid_std', 'spectral_spread_std', 'spectral_entropy_std',
        'spectral_flux_std', 'spectral_rolloff_std', 'mfcc_1_std', 'mfcc_2_std',
        'mfcc_3_std', 'mfcc_4_std', 'mfcc_5_std', 'mfcc_6_std', 'mfcc_7_std',
        'mfcc_8_std', 'mfcc_9_std', 'mfcc_10_std', 'mfcc_11_std', 'mfcc_12_std',
        'mfcc_13_std'
    ]

def process_audio_file(file_path: str) -> Tuple[np.ndarray, List[str]]:
    """Process a single audio file and return features with names"""
    try:
        # Read audio file - returns (sampling_rate, signal)
        fs, x = aIO.read_audio_file(file_path)
        
        # Convert to mono if stereo
        if len(x.shape) > 1:
            x = np.mean(x, axis=1)
        
        # Convert time parameters to samples
        mid_window = int(1.0 * fs)    # 1 second window
        mid_step = int(1.0 * fs)      # 1 second step
        short_window = int(0.05 * fs)  # 50ms window
        short_step = int(0.025 * fs)   # 25ms step
        
        # Extract features - returns (feature_matrix, feature_names)
        feature_matrix, _ = aF.mid_feature_extraction(
            x, fs, mid_window, mid_step, short_window, short_step
        )
        
        # Transpose the matrix to get features as columns
        return feature_matrix.T, get_feature_names()
    
    except Exception as e:
        logger.error(f"Error processing file {file_path}: {str(e)}")
        raise

@app.get("/profile-audio/{audio_path:path}")
async def profile_audio(audio_path: str) -> Dict[str, Any]:
    """Endpoint to profile audio files"""
    try:
        full_path = os.path.join(AUDIO_DIR, audio_path)
        
        if not os.path.exists(full_path):
            available = [f for f in os.listdir(AUDIO_DIR) if f.endswith(SUPPORTED_FORMATS)]
            return {
                "status": "error",
                "error": f"Path '{audio_path}' not found!",
                "available_files": available
            }

        # Process the audio file
        logger.info(f"Processing audio file: {full_path}")
        features, feature_names = process_audio_file(full_path)
        
        # Convert to DataFrame
        df = pd.DataFrame(features, columns=feature_names)

        # Generate gencrafter profile
        profile = why.log(df).profile()
        profile.set_dataset_timestamp(datetime.now(timezone.utc))

        # Prepare response
        return {
            "status": "success",
            "audio_path": audio_path,
            "features_extracted": len(feature_names),
      
            "feature_stats": {
                "mean_values": df.mean().to_dict(),
                "std_values": df.std().to_dict()
            }
        }

    except Exception as e:
        logger.error(f"Audio processing error: {str(e)}")
        return {
            "status": "error",
            "error": f"Audio processing failed: {str(e)}",
            "suggestion": "1. Install FFmpeg\n2. Check file is valid audio\n3. Verify file permissions"
        }