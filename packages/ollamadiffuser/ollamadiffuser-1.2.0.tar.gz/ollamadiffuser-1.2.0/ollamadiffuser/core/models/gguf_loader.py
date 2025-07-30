"""
GGUF Model Loader and Interface

This module provides support for loading and running GGUF quantized models,
specifically for FLUX.1-dev-gguf variants using stable-diffusion.cpp Python bindings.
"""

import os
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List, Union
import torch
from PIL import Image
import numpy as np

logger = logging.getLogger(__name__)

try:
    from stable_diffusion_cpp import StableDiffusion
    GGUF_AVAILABLE = True
    logger.info("stable-diffusion-cpp-python is available")
except ImportError:
    StableDiffusion = None
    GGUF_AVAILABLE = False
    logger.warning("stable-diffusion-cpp-python not available. GGUF models will not work.")

class GGUFModelLoader:
    """Loader for GGUF quantized diffusion models using stable-diffusion.cpp"""
    
    def __init__(self):
        self.model = None
        self.model_path = None
        self.model_config = None
        self.loaded_model_name = None
        self.stable_diffusion = None
        
    def is_gguf_model(self, model_name: str, model_config: Dict[str, Any]) -> bool:
        """Check if a model is a GGUF model"""
        variant = model_config.get('variant', '')
        return 'gguf' in variant.lower() or model_name.endswith('-gguf') or 'gguf' in model_name.lower()
    
    def get_gguf_file_path(self, model_dir: Path, variant: str) -> Optional[Path]:
        """Find the appropriate GGUF file based on variant"""
        if not model_dir.exists():
            return None
            
        # Map variant to actual file names
        variant_mapping = {
            'gguf-q2k': 'flux1-dev-Q2_K.gguf',
            'gguf-q3ks': 'flux1-dev-Q3_K_S.gguf', 
            'gguf-q4ks': 'flux1-dev-Q4_K_S.gguf',
            'gguf-q4-0': 'flux1-dev-Q4_0.gguf',
            'gguf-q4-1': 'flux1-dev-Q4_1.gguf',
            'gguf-q5ks': 'flux1-dev-Q5_K_S.gguf',
            'gguf-q5-0': 'flux1-dev-Q5_0.gguf',
            'gguf-q5-1': 'flux1-dev-Q5_1.gguf',
            'gguf-q6k': 'flux1-dev-Q6_K.gguf',
            'gguf-q8': 'flux1-dev-Q8_0.gguf',
            'gguf-f16': 'flux1-dev-F16.gguf',
            'gguf': 'flux1-dev-Q4_K_S.gguf',  # Default to Q4_K_S
        }
        
        filename = variant_mapping.get(variant.lower())
        if filename:
            gguf_file = model_dir / filename
            if gguf_file.exists():
                return gguf_file
        
        # Fallback: search for any .gguf file
        gguf_files = list(model_dir.glob('*.gguf'))
        if gguf_files:
            return gguf_files[0]  # Return first found
            
        return None
    
    def get_additional_model_files(self, model_dir: Path) -> Dict[str, Optional[Path]]:
        """Find additional model files required for FLUX GGUF inference"""
        files = {
            'vae': None,
            'clip_l': None,
            't5xxl': None
        }
        
        # Common file patterns for FLUX models
        vae_patterns = ['ae.safetensors', 'vae.safetensors', 'flux_vae.safetensors']
        clip_l_patterns = ['clip_l.safetensors', 'text_encoder.safetensors']
        t5xxl_patterns = ['t5xxl_fp16.safetensors', 't5xxl.safetensors', 't5_encoder.safetensors']
        
        # Search for VAE
        for pattern in vae_patterns:
            vae_file = model_dir / pattern
            if vae_file.exists():
                files['vae'] = vae_file
                break
        
        # Search for CLIP-L
        for pattern in clip_l_patterns:
            clip_file = model_dir / pattern
            if clip_file.exists():
                files['clip_l'] = clip_file
                break
                
        # Search for T5XXL
        for pattern in t5xxl_patterns:
            t5_file = model_dir / pattern
            if t5_file.exists():
                files['t5xxl'] = t5_file
                break
        
        return files
    
    def load_model(self, model_config: Dict[str, Any], model_name: str = None, model_path: Path = None) -> bool:
        """Load GGUF model using stable-diffusion.cpp"""
        # Extract parameters from model_config if not provided separately
        if model_name is None:
            model_name = model_config.get('name', 'unknown')
        if model_path is None:
            model_path = Path(model_config.get('path', ''))
        
        logger.info(f"Loading GGUF model: {model_name}")
        
        try:
            # Find the GGUF file
            gguf_files = list(model_path.glob("*.gguf"))
            if not gguf_files:
                logger.error(f"No GGUF files found in {model_path}")
                return False
            
            gguf_file = gguf_files[0]  # Use the first GGUF file found
            logger.info(f"Using GGUF file: {gguf_file}")
            
            # Download required components
            components = self.download_required_components(model_path)
            
            # Verify all components are available
            missing_components = [name for name, path in components.items() if path is None]
            if missing_components:
                logger.error(f"Missing required components: {missing_components}")
                return False
            
            # Initialize stable-diffusion.cpp
            if not GGUF_AVAILABLE:
                logger.error("stable-diffusion-cpp-python not properly installed")
                return False
                
            # Create StableDiffusion instance with correct API for FLUX
            # For FLUX models, use diffusion_model_path instead of model_path
            self.stable_diffusion = StableDiffusion(
                diffusion_model_path=str(gguf_file),  # FLUX GGUF models use this parameter
                vae_path=str(components['vae']),
                clip_l_path=str(components['clip_l']),
                t5xxl_path=str(components['t5xxl']),
                vae_decode_only=True,  # For txt2img only
                n_threads=-1  # Auto-detect threads
            )
            
            self.model_path = str(gguf_file)
            self.model_config = model_config
            self.loaded_model_name = model_name
            
            logger.info(f"Successfully loaded GGUF model: {model_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to load GGUF model {model_name}: {e}")
            if hasattr(self, 'stable_diffusion') and self.stable_diffusion:
                self.stable_diffusion = None
            return False
    
    def generate_image(self, prompt: str, **kwargs) -> Optional[Image.Image]:
        """Generate image using stable-diffusion.cpp FLUX inference"""
        if not self.stable_diffusion:
            logger.error("GGUF model not loaded")
            return None
        
        try:
            # Extract parameters with FLUX-optimized defaults
            # Support both parameter naming conventions for compatibility
            width = kwargs.get('width', 1024)
            height = kwargs.get('height', 1024)
            
            # Support both 'steps' and 'num_inference_steps'
            steps = kwargs.get('steps') or kwargs.get('num_inference_steps', 20)  # Increased for better quality
            
            # Support both 'cfg_scale' and 'guidance_scale' - FLUX works best with low CFG
            cfg_scale = kwargs.get('cfg_scale') or kwargs.get('guidance_scale', 1.0)  # FLUX optimized CFG (reduced from 1.2)
            
            seed = kwargs.get('seed', 42)
            negative_prompt = kwargs.get('negative_prompt', "")
            
            # Allow custom sampler, with FLUX-optimized default
            sampler = kwargs.get('sampler', kwargs.get('sample_method', 'dpmpp2m'))  # Better sampler for FLUX (fixed name)
            
            # Validate sampler and provide fallback
            valid_samplers = ['euler_a', 'euler', 'heun', 'dpm2', 'dpmpp2s_a', 'dpmpp2m', 'dpmpp2mv2', 'ipndm', 'ipndm_v', 'lcm', 'ddim_trailing', 'tcd']
            if sampler not in valid_samplers:
                logger.warning(f"Invalid sampler '{sampler}', falling back to 'dpmpp2m'")
                sampler = 'dpmpp2m'
            
            logger.info(f"Generating image: {width}x{height}, steps={steps}, cfg={cfg_scale}, sampler={sampler}, negative_prompt={negative_prompt}")
            
            # Log model quantization info for quality assessment
            if hasattr(self, 'model_path'):
                if 'Q2' in str(self.model_path):
                    logger.warning("Using Q2 quantization - expect lower quality. Consider Q4_K_S or higher for better results.")
                elif 'Q3' in str(self.model_path):
                    logger.info("Using Q3 quantization - moderate quality. Consider Q4_K_S or higher for better results.")
                elif 'Q4' in str(self.model_path):
                    logger.info("Using Q4 quantization - good balance of quality and size.")
                elif any(x in str(self.model_path) for x in ['Q5', 'Q6', 'Q8', 'F16']):
                    logger.info("Using high precision quantization - excellent quality expected.")
            
            # Generate image using stable-diffusion.cpp
            # According to the documentation, txt_to_img returns a list of PIL Images
            try:
                result = self.stable_diffusion.txt_to_img(
                    prompt=prompt,
                    negative_prompt=negative_prompt if negative_prompt else "",
                    cfg_scale=cfg_scale,
                    width=width,
                    height=height,
                    sample_method=sampler,  # Use optimized sampler
                    sample_steps=steps,
                    seed=seed
                )
                logger.info(f"txt_to_img returned: {type(result)}, length: {len(result) if result else 'None'}")
            except Exception as e:
                logger.error(f"txt_to_img call failed: {e}")
                return None
            
            if not result:
                logger.error("txt_to_img returned None")
                return None
                
            if not isinstance(result, list) or len(result) == 0:
                logger.error(f"txt_to_img returned unexpected format: {type(result)}")
                return None
            
            # Get the first PIL Image from the result list
            image = result[0]
            logger.info(f"Retrieved PIL Image: {type(image)}")
            
            # Verify it's a PIL Image
            if not hasattr(image, 'save'):
                logger.error(f"Result[0] is not a PIL Image: {type(image)}")
                return None
            
            # Optionally save a copy for debugging/history
            try:
                from ..config.settings import settings
                output_dir = settings.config_dir / "outputs"
                output_dir.mkdir(exist_ok=True)
                
                output_path = output_dir / f"gguf_output_{seed}.png"
                image.save(output_path)
                logger.info(f"Generated image also saved to: {output_path}")
            except Exception as e:
                logger.warning(f"Failed to save debug copy: {e}")
            
            # Return the PIL Image directly for API compatibility
            logger.info("Returning PIL Image for API use")
            return image
            
        except Exception as e:
            logger.error(f"Failed to generate image with GGUF model: {e}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            return None
    
    def unload_model(self):
        """Unload the GGUF model"""
        if self.stable_diffusion:
            try:
                # stable-diffusion-cpp handles cleanup automatically
                self.stable_diffusion = None
                self.model_path = None
                self.model_config = None
                self.loaded_model_name = None
                logger.info("GGUF model unloaded")
            except Exception as e:
                logger.error(f"Error unloading GGUF model: {e}")
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the loaded model"""
        if not self.stable_diffusion:
            return {
                'gguf_available': GGUF_AVAILABLE,
                'loaded': False
            }
            
        return {
            'type': 'gguf',
            'variant': self.model_config.get('variant', 'unknown'),
            'path': str(self.model_path),
            'name': self.loaded_model_name,
            'loaded': True,
            'gguf_available': GGUF_AVAILABLE,
            'backend': 'stable-diffusion.cpp'
        }
    
    def is_loaded(self) -> bool:
        """Check if a model is loaded"""
        return self.stable_diffusion is not None

    def get_gguf_download_patterns(self, variant: str) -> Dict[str, List[str]]:
        """Get file patterns for downloading specific GGUF variant
        
        Args:
            variant: Model variant (e.g., 'gguf-q4-1', 'gguf-q4ks')
            
        Returns:
            Dict with 'allow_patterns' and 'ignore_patterns' lists
        """
        # Map variant to specific GGUF file patterns
        variant_patterns = {
            'gguf-q2k': ['*Q2_K*.gguf'],
            'gguf-q3ks': ['*Q3_K_S*.gguf'], 
            'gguf-q4-0': ['*Q4_0*.gguf'],
            'gguf-q4-1': ['*Q4_1*.gguf'],
            'gguf-q4ks': ['*Q4_K_S*.gguf'],
            'gguf-q5-0': ['*Q5_0*.gguf'],
            'gguf-q5-1': ['*Q5_1*.gguf'],
            'gguf-q5ks': ['*Q5_K_S*.gguf'],
            'gguf-q6k': ['*Q6_K*.gguf'],
            'gguf-q8-0': ['*Q8_0*.gguf'],
            'gguf-f16': ['*F16*.gguf']
        }
        
        # Get the specific GGUF file pattern for this variant
        gguf_pattern = variant_patterns.get(variant, ['*.gguf'])
        
        # Essential files to download
        essential_files = [
            # Configuration and metadata
            'model_index.json',
            'README.md',
            'LICENSE*',
            '.gitattributes',
            'config.json',
        ]
        
        # Include the specific GGUF model file
        allow_patterns = essential_files + gguf_pattern
        
        # Create ignore patterns - ignore all other GGUF variants
        all_gguf_variants = []
        for pattern_list in variant_patterns.values():
            all_gguf_variants.extend(pattern_list)
        
        # Remove the current variant from ignore list
        ignore_patterns = [p for p in all_gguf_variants if p not in gguf_pattern]
        
        return {
            'allow_patterns': allow_patterns,
            'ignore_patterns': ignore_patterns
        }
    
    def download_required_components(self, model_path: Path) -> Dict[str, Optional[Path]]:
        """Download or locate required VAE, CLIP-L, and T5XXL components
        
        For FLUX GGUF models, these components need to be downloaded separately:
        - VAE: ae.safetensors from black-forest-labs/FLUX.1-dev
        - CLIP-L: clip_l.safetensors from comfyanonymous/flux_text_encoders
        - T5XXL: t5xxl_fp16.safetensors from comfyanonymous/flux_text_encoders
        """
        from ..utils.download_utils import robust_snapshot_download
        from ..config.settings import settings
        
        components = {
            'vae': None,
            'clip_l': None, 
            't5xxl': None
        }
        
        logger.info("Downloading required FLUX components...")
        
        try:
            # Download VAE from official FLUX repository
            vae_dir = model_path.parent / "flux_vae"
            if not (vae_dir / "ae.safetensors").exists():
                logger.info("Downloading FLUX VAE...")
                robust_snapshot_download(
                    repo_id="black-forest-labs/FLUX.1-dev",
                    local_dir=str(vae_dir),
                    cache_dir=str(settings.cache_dir),
                    allow_patterns=['ae.safetensors'],
                    max_retries=3
                )
            
            vae_path = vae_dir / "ae.safetensors"
            if vae_path.exists():
                components['vae'] = vae_path
                logger.info(f"VAE found at: {vae_path}")
            
            # Download text encoders
            text_encoders_dir = model_path.parent / "flux_text_encoders"
            
            # Download CLIP-L
            if not (text_encoders_dir / "clip_l.safetensors").exists():
                logger.info("Downloading CLIP-L text encoder...")
                robust_snapshot_download(
                    repo_id="comfyanonymous/flux_text_encoders",
                    local_dir=str(text_encoders_dir),
                    cache_dir=str(settings.cache_dir),
                    allow_patterns=['clip_l.safetensors'],
                    max_retries=3
                )
            
            clip_l_path = text_encoders_dir / "clip_l.safetensors"
            if clip_l_path.exists():
                components['clip_l'] = clip_l_path
                logger.info(f"CLIP-L found at: {clip_l_path}")
            
            # Download T5XXL  
            if not (text_encoders_dir / "t5xxl_fp16.safetensors").exists():
                logger.info("Downloading T5XXL text encoder...")
                robust_snapshot_download(
                    repo_id="comfyanonymous/flux_text_encoders", 
                    local_dir=str(text_encoders_dir),
                    cache_dir=str(settings.cache_dir),
                    allow_patterns=['t5xxl_fp16.safetensors'],
                    max_retries=3
                )
            
            t5xxl_path = text_encoders_dir / "t5xxl_fp16.safetensors"
            if t5xxl_path.exists():
                components['t5xxl'] = t5xxl_path
                logger.info(f"T5XXL found at: {t5xxl_path}")
                
        except Exception as e:
            logger.error(f"Failed to download FLUX components: {e}")
            
        return components


# Global GGUF loader instance
gguf_loader = GGUFModelLoader() 