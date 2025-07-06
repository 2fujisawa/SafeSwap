# SafeSwap

SafeSwap is an award-winning project developed for Chapman's 2025 Hackathon! 🏆  
This app uses computer vision with YOLOv8 to detect microplastics in everyday objects.

---

## 🥇 Hackathon Highlights

- 🎉 **Winner of First Place** at Chapman's Hackathon 2025.
- 🏅 Recognized for innovative use of AI for environmental impact.
- 🖼️ _(Add photos below of you and your team winning, the prize ceremony, and your prize!)_

---

## 📸 Demo & Media



<style>
  .slideshow-container {
    position: relative;
    max-width: 300px;
    margin: auto;
  }

  .slides {
    display: none;
    width: 100%;
  }

  .fade {
    animation-name: fade;
    animation-duration: 1s;
  }

  @keyframes fade {
    from {opacity: .4}
    to {opacity: 1}
  }
</style>

<div class="slideshow-container">
  <img class="slides fade" src="images/homepage.jpeg" alt="Home Page" />
  <img class="slides fade" src="images/winner1.JPG" alt="Winning Photo 1" />
  <img class="slides fade" src="images/winner234.jpeg" alt="Winning Photo 2" />
</div>

<script>
  let slideIndex = 0;
  showSlides();

  function showSlides() {
    let i;
    let slides = document.getElementsByClassName("slides");
    for (i = 0; i < slides.length; i++) {
      slides[i].style.display = "none";
    }
    slideIndex++;
    if (slideIndex > slides.length) {slideIndex = 1}
    slides[slideIndex-1].style.display = "block";
    setTimeout(showSlides, 1000); // Change image every 1 second
  }
</script>

🎥 **Live Demo Video:**  
[Watch how SafeSwap works in real time!](https://youtu.be/fTq29E8R6cs)

🔗 **Check out our LinkedIn feature:**  
[Chapman CS Club PantherHacks Post](https://www.linkedin.com/posts/chapman-computer-science-club_pantherhacks-pantherhacks2025-hackathon-ugcPost-7322712880305295361-AoyD?utm_source=share&utm_medium=member_desktop&rcm=ACoAAERIrrMBhpriHi6tBcmDMns7PLOnGhRIStE)

---

## 🚀 What is SafeSwap?

SafeSwap uses YOLOv8 object detection to identify common household objects and estimate the amount of microplastics associated with each item.  
It’s designed to raise awareness about microplastic pollution through interactive scanning.

---

## ⚡️ How to Run It

1. **Clone this repository**
   ```bash
   git clone https://github.com/2fujisawa/safeswap.git
   cd safeswap
   ```

2. **Set up your virtual environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the app**
   ```bash
   python app.py
   ```
   Open your browser at [http://127.0.0.1:5000](http://127.0.0.1:5000)

---

_✨ Proudly built by Linus Fujisawa for Chapman’s Hackathon 2025_
