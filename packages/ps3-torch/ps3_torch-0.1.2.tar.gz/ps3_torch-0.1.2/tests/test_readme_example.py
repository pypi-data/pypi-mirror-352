from PIL import Image
from ps3 import PS3VisionModel, PS3ImageProcessor

# Load the PS3 model and processor.
vision_model = PS3VisionModel.from_pretrained("/home/baifengs/baifengs/projects/open_clip/hf_ckpt/250325_1632")
processor = PS3ImageProcessor.from_pretrained("/home/baifengs/baifengs/projects/open_clip/hf_ckpt/250325_1632")
vision_model.cuda().eval()

# You can replace it with your own image.
image = Image.open("assets/test_images/dock.jpg")

# Preprocess the image.
x = processor(image)["pixel_values"][0].unsqueeze(0).cuda()

outs = vision_model(x, num_look_close="all")
features = outs.last_hidden_state
print(features.shape)  # (1, 88209, 1152)

outs = vision_model(x, num_look_close=2)
features = outs.last_hidden_state
print(features.shape)  # (1, 5849, 1152)

outs = vision_model(x, num_token_look_close=3000)
features = outs.last_hidden_state
print(features.shape)  # (1, 3729, 1152)


from torchvision import transforms
import numpy as np
import os
import cv2
import matplotlib.pyplot as plt
from scipy.ndimage import gaussian_filter

def create_heatmap_overlay(image, heatmap, alpha=0.4, colormap=plt.cm.jet, sigma=10.0):
    if len(image.shape) == 2:
        image = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)

    smoothed_heatmap = gaussian_filter(heatmap.astype(np.float32), sigma=sigma)
    smoothed_heatmap = (smoothed_heatmap - smoothed_heatmap.min()) / \
                      (smoothed_heatmap.max() - smoothed_heatmap.min())
    colored_heatmap = (colormap(smoothed_heatmap) * 255).astype(np.uint8)
    
    if colored_heatmap.shape[-1] == 4:
        colored_heatmap = colored_heatmap[:, :, :3]
    
    overlay = cv2.addWeighted(image, 1 - alpha, colored_heatmap, alpha, 0)
    return Image.fromarray(overlay)

def save_visualization(selection_probs, image, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    resize_transform = transforms.Resize(image.size[::-1])
    for i, prob in enumerate(selection_probs):
        prob = (prob - prob.min()) / (prob.max() - prob.min() + 1e-6)
        prob = resize_transform(prob)
        prob = prob.squeeze(0).detach().cpu().numpy()
        # overlay the selection probability map on the original image
        # overlay = Image.fromarray((np.array(image) * prob[:, :, None]).astype(np.uint8))
        overlay = create_heatmap_overlay(np.array(image), prob)
        overlay.save(os.path.join(output_dir, f"selection_prob_scale_{i}.png"))
    image.save(os.path.join(output_dir, f"image.png"))

selection_probs = outs.selection_probs
print([p.shape for p in selection_probs])  # [(1, 54, 54), (1, 108, 108), (1, 270, 270)]
save_visualization(selection_probs, image, "output/bottom_up_selection_probs")



from ps3 import PS3Tokenizer, PS3TextModel

tokenizer = PS3Tokenizer.from_pretrained("/home/baifengs/baifengs/projects/open_clip/hf_ckpt/250325_1632")
text_model = PS3TextModel.from_pretrained("/home/baifengs/baifengs/projects/open_clip/hf_ckpt/250325_1632")
text_model.cuda().eval()

text = ["A tall spire with a cross at the top of the building."]
text = tokenizer(text).cuda()
prompt = text_model(text).prompt


outs = vision_model(x, num_look_close=2, prompt=prompt)
features = outs.last_hidden_state
print(features.shape)  # (1, 5849, 1152)

selection_probs = outs.selection_probs
save_visualization(selection_probs, image, "output/top_down_selection_probs_1")


text = ["A green rope on the green and red boat."]
text = tokenizer(text).cuda()
prompt = text_model(text).prompt
outs = vision_model(x, num_look_close=2, prompt=prompt)
selection_probs = outs.selection_probs
save_visualization(selection_probs, image, "output/top_down_selection_probs_2")


feature_maps = vision_model.vision_model.format_features_into_feature_maps(outs.last_hidden_state, outs.selection_maps)
print([x.shape for x in feature_maps])  # [(1, 1152, 27, 27), (1, 1152, 54, 54), (1, 1152, 108, 108), (1, 1152, 270, 270)]
