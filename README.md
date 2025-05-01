## Patch notes only if using original app.py

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

**The WebUI takes time to show up. Take it easy.**



## MPS compatibility   
Replace your local app.py   
with the one (app_mps_optimized.py) nested in app folder, and  
Rename it as app.py  

Restart  


## Batch Caption  
 **(Sample terminal log is provided for your reference)**  
* Download florence2_batch_caption.py and place it anywhere in your computer   
* Ensure your Florence2 (the Pinokio app) is up and run (the WebUI shows up)  
* Open your terminal  and place it anywhere in your computer (ie. .../Downloads)   
* Ensure your Florence2 (the Pinokio app) is up and run (the WebUI show up)  
* Open your terminal (for rest of steps from a to f)  
* a. Get into the virtual environment and input
  	```
  	source .../pinokio/api/florence2.git/app/env/bin/activate 
  	```  
* b. Locate the folder where your florence2_batch_caption.py is placed  
  ie. cd ~/Downloads  
* c. Run the script  
  ```
  python florence2_batch_caption.py
  ```
* d. Choose the type of caption when asked
  1: Standard Caption  
	2: Detailed Caption  
	3: More Detailed Caption  
* e. Enter the full path to the folder containing your images when asked  
* f. Wait for its completion  
* Two types of files generated in the folder provided by step e:  
	1: a summary .csv file    
	2: indiviual .txt file(s) containing caption associated with each indiviual image  
    
 **Now it is ready for your Lora training.**
    
