sdjfkfnejwnfwjdnjnfsjkjknfjknkhwiuefhhdsjkhfjdsvskjbvkdjsbcjkmkjzandvkjsnckzvnd = 'none'
def authenticate(paff):
   import sys
   if paff != "agamjot0000":
       print("Wrong password")
       raise Exception("Wrong password")
       sys.exit(1)
      
   else:
       print("Correct password, proceeding with the script...")
       sdjfkfnejwnfwjdnjnfsjkjknfjknkhwiuefhhdsjkhfjdsvskjbvkdjsbcjkmkjzandvkjsnckzvnd = 'yeeeeeesir'




def IMGGEN(prompt):
   import sys
   if sdjfkfnejwnfwjdnjnfsjkjknfjknkhwiuefhhdsjkhfjdsvskjbvkdjsbcjkmkjzandvkjsnckzvnd == 'none':
       print("You need to authenticate first!")
       raise Exception("You need to authenticate first!")
       sys.exit(1)
   elif sdjfkfnejwnfwjdnjnfsjkjknfjknkhwiuefhhdsjkhfjdsvskjbvkdjsbcjkmkjzandvkjsnckzvnd == 'yeeeeeesir':
       print("Generating image...")
       from huggingface_hub import InferenceClient
       apoo = ['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', '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', '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', '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', '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', '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', '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', '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', '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', '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']
       apoo = iter(apoo)
       while True:
           try:
               client = InferenceClient(
                   provider="replicate",
                   api_key=next(apoo),
               )


               # output is a PIL.Image object
               image = client.text_to_image(
                   f"{prompt}",
                   model="stabilityai/stable-diffusion-3.5-large",
               )




              
              
               return image
              
           except StopIteration as e:
               apoo = iter(apoo)
           except:
               pass




  






def IMGANALIZE(file_location):
   import sys
   if sdjfkfnejwnfwjdnjnfsjkjknfjknkhwiuefhhdsjkhfjdsvskjbvkdjsbcjkmkjzandvkjsnckzvnd == 'none':
       print("You need to authenticate first!")
       raise Exception("You need to authenticate first!")
       sys.exit(1)
   elif sdjfkfnejwnfwjdnjnfsjkjknfjknkhwiuefhhdsjkhfjdsvskjbvkdjsbcjkmkjzandvkjsnckzvnd == 'yeeeeeesir':


       # Use a pipeline as a high-level helper
       from transformers import pipeline
       pipe = pipeline("image-to-text", model="Salesforce/blip-image-captioning-large")
       from PIL import Image
       wf = Image.open(file_location)
       caption = pipe(wf)
       return caption[0]['generated_text']





