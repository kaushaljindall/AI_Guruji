import os
import subprocess
import torch

class AvatarService:
    def __init__(self):
        self.output_dir = os.path.join(os.getcwd(), "data", "outputs", "avatar")
        self.weights_dir = os.path.join(os.getcwd(), "data", "weights")
        self.base_avatar_path = os.path.join(os.getcwd(), "data", "avatar", "teacher_base.mp4")
        self.wav2lip_path = os.path.join(os.getcwd(), "Wav2Lip") # Assumes Wav2Lip repo is cloned here
        os.makedirs(self.output_dir, exist_ok=True)

    def verify_setup(self):
        """Checks if Wav2Lip weights and base video exist."""
        checkpoint = os.path.join(self.weights_dir, "wav2lip_gan.pth")
        if not os.path.exists(checkpoint):
            return False, f"Missing Checkpoint: {checkpoint}"
        if not os.path.exists(self.base_avatar_path):
            return False, f"Missing Base Avatar: {self.base_avatar_path}"
        if not os.path.exists(os.path.join(self.wav2lip_path, "inference.py")):
            return False, f"Missing Wav2Lip Repository at {self.wav2lip_path}"
        return True, "Setup Complete"

    def generate_lip_sync(self, audio_path: str, output_filename: str) -> str:
        """
        Runs Wav2Lip inference to sync the base avatar with the provided audio.
        """
        is_valid, msg = self.verify_setup()
        if not is_valid:
            raise RuntimeError(f"Avatar Service Not Ready: {msg}")

        output_path = os.path.join(self.output_dir, output_filename)
        checkpoint_path = os.path.join(self.weights_dir, "wav2lip_gan.pth")

        # Construct command to run external Wav2Lip inference
        # This assumes the standard Wav2Lip inference arguments
        command = [
            "python", 
            os.path.join(self.wav2lip_path, "inference.py"),
            "--checkpoint_path", checkpoint_path,
            "--face", self.base_avatar_path,
            "--audio", audio_path,
            "--outfile", output_path,
            "--resize_factor", "1",
            "--nosmooth"
        ]

        print(f"Running Wav2Lip: {' '.join(command)}")
        try:
            # Run inference (this might take time)
            subprocess.run(command, check=True, cwd=self.wav2lip_path)
            return output_path
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Wav2Lip failed: {str(e)}")

avatar_service = AvatarService()
