import deepgram
import inspect

# Check listen v1
if hasattr(deepgram, 'listen') and hasattr(deepgram.listen, 'v1'):
    print("\n--- deepgram.listen.v1 Attributes ---")
    print(dir(deepgram.listen.v1))
    
    if hasattr(deepgram.listen.v1, 'LiveOptions'):
         print("\n✅ LiveOptions found in deepgram.listen.v1")

# Check speak v1
if hasattr(deepgram, 'speak') and hasattr(deepgram.speak, 'v1'):
    print("\n--- deepgram.speak.v1 Attributes ---")
    print(dir(deepgram.speak.v1))
