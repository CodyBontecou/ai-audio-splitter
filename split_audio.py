import os
import librosa
import torchaudio
import torch

def save_audio(file_name, tensor, sample_rate):
    # This function converts a PyTorch Tensor into NumPy array and writes it back as a .wav file using torchaudio.save(). 
    # It also handles converting from mono to stereo for consistency with the original audio.

    if tensor.shape[0] == 1:
        tensor = torch.cat([tensor, tensor], dim=0)

    torchaudio.save(file_name, tensor, sample_rate)

def batch(file_path:str, out_dir:str, batch_duration:int = 200):
    """
        Split audio with duration and save it to files
        file_path: path to audio
        out_dir: output directory for the split audio files
        batch_duration: duration to split, default is 2 seconds
    """
    
    if not os.path.exists(out_dir):
      os.makedirs(out_dir)
      
    audio_duration = librosa.get_duration(path=file_path)
    audio, sample_rate = torchaudio.load(file_path)
    
    start_duration = 0
    idx = 1 # initialize the index for output files 

    while True:
        end_duration = start_duration + batch_duration
        
        is_stop = end_duration > audio_duration
      
        if not is_stop:  
            out_file = os.path.join(out_dir, f"split_{idx}.wav") # create the output filename
            
            save_audio(out_file, 
                       audio[:, start_duration * sample_rate: end_duration * sample_rate], 
                        sample_rate)  
             
            idx += 1   
            start_duration = end_duration
        else:
            out_file = os.path.join(out_dir, f"split_{idx}.wav") # create the output filename
            
            save_audio(out_file, 
                       audio[:, start_duration * sample_rate:], 
                        sample_rate)  
              
            break   
        
# usage
batch('samples/happy-path.mp3', 'hp-output')