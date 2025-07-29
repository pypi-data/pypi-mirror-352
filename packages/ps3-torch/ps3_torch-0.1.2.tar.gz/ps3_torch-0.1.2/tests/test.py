from ps3.modeling_ps3 import PS3VisionModel, PS3TextModel, PS3Model
from ps3.image_processing_ps3 import PS3ImageProcessor
from ps3.tokenization_ps3 import PS3Tokenizer
from transformers import AutoTokenizer
from safetensors.torch import load_file
import torch
from open_clip import create_model_from_pretrained, get_tokenizer
from PIL import Image

# # Load HF model
# vision_model = PS3VisionModel.from_pretrained("/home/baifengs/baifengs/projects/open_clip/hf_ckpt/250123_1112_retrain").cuda()
# text_model = PS3TextModel.from_pretrained("/home/baifengs/baifengs/projects/open_clip/hf_ckpt/250123_1112_retrain").cuda()
# processor = PS3ImageProcessor.from_pretrained("/home/baifengs/baifengs/projects/open_clip/hf_ckpt/250123_1112_retrain")
# tokenizer = PS3Tokenizer.from_pretrained("/home/baifengs/baifengs/projects/open_clip/hf_ckpt/250123_1112_retrain")
# vision_model.vision_model.num_hidden_layers_to_return = 2

# Load HF model
vision_model = PS3VisionModel.from_pretrained("Efficient-Large-Model/PS3-1.5K-SigLIP").cuda()
text_model = PS3TextModel.from_pretrained("Efficient-Large-Model/PS3-1.5K-SigLIP").cuda()
processor = PS3ImageProcessor.from_pretrained("Efficient-Large-Model/PS3-1.5K-SigLIP")
tokenizer = PS3Tokenizer.from_pretrained("Efficient-Large-Model/PS3-1.5K-SigLIP")
vision_model.vision_model.num_hidden_layers_to_return = 2

# Load OpenCLIP model
openclip_model, openclip_processor = create_model_from_pretrained("ViT-SO400M-14-SigLIP-384-S3-1536-2560token-nonlinear_proj-kvcache-separate_pos_emb-highdim_highres_select", 
                                                                  "/home/baifengs/baifengs/projects/open_clip/output/250123_1112_retrain/checkpoints/epoch_latest.pt", load_weights_only=False)
openclip_model = openclip_model.cuda()
openclip_tokenizer = get_tokenizer("ViT-SO400M-14-SigLIP-384-S3-1536-2560token-nonlinear_proj-kvcache-separate_pos_emb-highdim_highres_select")
openclip_vision_model = openclip_model.visual
openclip_text_model = openclip_model.text
openclip_vision_model.num_hidden_layers_to_return = 2

# Load image
image = Image.open("/home/baifengs/baifengs/projects/open_clip/tests/images/cat_and_dog.png")

# Test if output aligns for bottom-up selection
openclip_x = openclip_processor(image).unsqueeze(0).cuda()
openclip_out, _, __ = openclip_vision_model(openclip_x, num_look_close=2, output_hidden_states=True)
x = processor(image)["pixel_values"][0].unsqueeze(0).cuda()
out = vision_model(x, num_look_close=2).hidden_states
for a, b in zip(out, openclip_out):
    print(torch.allclose(a, b))
    if not torch.allclose(a, b):
        print(a)
        print(b)

# Test if output aligns for top-down selection
openclip_text = ["a photo of a cat"]
openclip_text = openclip_tokenizer(openclip_text).cuda()
openclip_prompt = openclip_model.prompt_proj(openclip_model.encode_text(openclip_text, normalize=True))
openclip_x = openclip_processor(image).unsqueeze(0).cuda()
openclip_out, _, __ = openclip_vision_model(openclip_x, num_look_close=2, prompt=openclip_prompt, output_hidden_states=True)


text = ["a photo of a cat"]
text = tokenizer(text).cuda()
prompt = text_model(text).prompt
x = processor(image)["pixel_values"][0].unsqueeze(0).cuda()
out = vision_model(x, num_look_close=2, prompt=prompt).hidden_states

for a, b in zip(out, openclip_out):
    print(torch.allclose(a, b))
    if not torch.allclose(a, b):
        print(a)
        print(b)

# vision_model.save_pretrained("./tmp")
# text_model.save_pretrained("./tmp")
# processor.save_pretrained("./tmp")
# tokenizer.save_pretrained("./tmp")
