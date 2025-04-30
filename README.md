# Patch notes only

Your may need this if your installtion or reset or WebUI fails.

Let installation or reset fail or stop it.
* Open Terminal, source .../pinokio/api/florence2.git/app//env/bin/activate.
* ```
  pip install transformers einops timm
  ```
  (this will get the standard, working versions).
* ```
  pip install --upgrade gradio gradio_client
  ```
   (to get the version that fixed the TypeError).
* Download frpc_darwin_arm64 (Download here [link](https://cdn-media.huggingface.co/frpc-gradio-0.2/frpc_darwin_arm64 "Title")),   
  rename it to frpc_darwin_arm64_v0.2, and   
  move it to the .../pinokio/api/florence2.git/app/env/lib/python3.10/site-packages/gradio/ folder. 

All patched, restart.

# The WebUI takes time to show up. Take it easy. 
