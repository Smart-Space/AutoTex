import torch
import argparse
from PIL import Image, ImageStat, ImageOps

import data

device=None
model=None
vis_processor=None

def load_model():
    global device, model, vis_processor

    import unimernet.tasks as tasks
    from unimernet.common.config import Config
    from unimernet.processors import load_processor

    device=torch.device("cuda" if torch.cuda.is_available() else "cpu")
    args = argparse.Namespace(cfg_path="./configs/demo.yaml", options=None)
    cfg = Config(args)
    task = tasks.setup_task(cfg)
    model = task.build_model(cfg).to(device)
    vis_processor = load_processor(
        "formula_image_eval",
        cfg.config.datasets.formula_rec_eval.vis_processor.eval,
    )
    data.root.event_generate("<<ModelLoaded>>")

def process_img():
    if model is None or vis_processor is None:
        return
    img=data.orimg.convert("RGB")
    if data.reverse == 0:
        # 自动判断
        image=img.convert("L")
        mean_pixel=int(ImageStat.Stat(image).mean[0])
        histogram=image.histogram()
        dark_pixels=sum(histogram[:mean_pixel])
        light_pixels=sum(histogram[mean_pixel:])
        if dark_pixels > light_pixels:
            img=ImageOps.invert(img)
            data.root.event_generate("<<ImageInverted>>")
        else:
            data.root.event_generate("<<ImageNotInverted>>")
    elif data.reverse == 1:
        img=ImageOps.invert(img)
    
    image_tensor=vis_processor(img).unsqueeze(0).to(device)
    with torch.no_grad():
        output=model.generate({"image": image_tensor})
    data.latexstring=output["pred_str"][0]
    data.root.event_generate("<<ImageProcessed>>")
