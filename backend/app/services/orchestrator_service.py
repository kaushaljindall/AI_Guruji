import re
import json
import asyncio
from typing import List, Dict
import concurrent.futures

class OrchestratorService:
    def parse_llm_output(self, llm_text: str) -> List[Dict]:
        """
        Parses the structured text output from the LLM into a list of scene objects.
        Expected format is specific sections for SLIDE X: HEADING, SCRIPT, etc.
        """
        scenes = []
        
        # Regex to find slide blocks. 
        # This assumes the LLM strictly follows the requested format:
        # SLIDE X:
        # HEADING: ...
        # ...
        # SCRIPT: ...
        
        slide_pattern = re.compile(r"SLIDE \d+:(.*?)((?=SLIDE \d+:)|$)", re.DOTALL)
        matches = slide_pattern.findall(llm_text)

        for i, match in enumerate(matches):
            content = match[0] if isinstance(match, tuple) else match
            
            # Extract attributes
            heading_match = re.search(r"HEADING:\s*(.*)", content)
            script_match = re.search(r"SCRIPT(?:\s*\(spoken, teacher-style\))?:\s*(.*)", content, re.DOTALL)
            points_match = re.search(r"IMPORTANT POINTS:\s*(.*)", content, re.DOTALL)
            
            heading = heading_match.group(1).strip() if heading_match else f"Slide {i+1}"
            
            # For script, we need to stop before the next dash line or end
            script_raw = script_match.group(1).strip() if script_match else ""
            # Cleanup script (remove trailing dashes or next section headers if regex leaked)
            slide_script = script_raw.split("----------------------------------------------------")[0].strip()
            
            # For HTML generation (Simple Template based on heading/points)
            # In a real scenario, LLM could generate HTML directly. 
            # Here we wrap the content in a simple HTML structure for the SlideService
            
            points_raw = points_match.group(1).split("SCRIPT")[0].strip() if points_match else ""
            points_list = [p.strip().strip('- ') for p in points_raw.split('\n') if p.strip()]
            points_html = "".join([f"<li style='font-size: 24px; margin-bottom: 20px;'>{p}</li>" for p in points_list])
            
            html_content = f"""
            <div style="background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%); color: white; width: 100%; height: 100%; padding: 80px; font-family: 'Segoe UI', sans-serif; display: flex; flex-col; justify-content: center;">
                <h1 style="font-size: 60px; color: #60a5fa; margin-bottom: 40px; border-bottom: 2px solid #334155; padding-bottom: 20px;">{heading}</h1>
                <ul style="line-height: 1.6;">
                    {points_html}
                </ul>
                <div style="position: absolute; bottom: 40px; right: 60px; font-size: 18px; color: #94a3b8;">AI Guruji Lecture Series</div>
            </div>
            """

            scenes.append({
                "scene_id": i + 1,
                "heading": heading,
                "script": slide_script,
                "html_content": html_content
            })
            
        return scenes

    async def execute_pipeline(self, 
                               llm_text: str, 
                               slide_service, 
                               tts_service, 
                               avatar_service) -> List[Dict]:
        """
        Takes the LLM text, parses it, and runs generation for each scene.
        """
        scenes = self.parse_llm_output(llm_text)
        
        results = []
        loop = asyncio.get_running_loop()
        
        # Use a ThreadPoolExecutor for blocking calls (TTS)
        with concurrent.futures.ThreadPoolExecutor() as pool:
            for scene in scenes:
                print(f"Processing Scene {scene['scene_id']}...")
                
                # 1. Generate Slide Image (Async - Playwright)
                try:
                    slide_path = await slide_service.generate_slide_image(scene["html_content"])
                    slide_url = f"/files/slides/{os.path.basename(slide_path)}"
                except Exception as e:
                    print(f"Error generating slide for Scene {scene['scene_id']}: {e}")
                    slide_url = None
                
                # 2. Generate Audio (Blocking - run in thread)
                audio_filename = f"scene_{scene['scene_id']}_{int(asyncio.get_event_loop().time())}.wav"
                audio_url = None
                duration = 0
                
                try:
                    # Run synchronos TTS generation in a separate thread to avoid blocking main loop
                    audio_path, duration = await loop.run_in_executor(
                        pool, 
                        tts_service.generate_audio, 
                        scene["script"], 
                        audio_filename
                    )
                    audio_url = f"/files/audio/{os.path.basename(audio_path)}"
                except Exception as e:
                    print(f"Error generating audio for Scene {scene['scene_id']}: {e}")

                # 3. Generate Lip Sync Video (Optional)
                # ... skipping for now as per previous logic ...

                results.append({
                    "scene_id": scene['scene_id'],
                    "slide_url": slide_url,
                    "audio_url": audio_url,
                    "duration": duration,
                    "script": scene['script'],
                    # "avatar_url": ...
                })
            
        return results

import os
orchestrator_service = OrchestratorService()
