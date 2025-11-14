from engine.post_generator import generate_post
from engine.utils import log

def main():
    topic = "Example topic for testing the engine"
    
    post = generate_post(topic)

    log("Generated Post:")
    log(post)

if __name__ == "__main__":
    main()
