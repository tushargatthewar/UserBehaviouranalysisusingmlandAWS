$(document).ready(function() {
    const CTB_ImagesUrl = fetch("SISDP/CSV/Atlas_slider.csv")
      .then((response) => response.text())
      .then((t) => {
        return t.split(',').map(filename => filename.trim());
      });

    const CTB_UrlArray = async () => {
      const filename = await CTB_ImagesUrl;  
      return filename;
    };

    CTB_UrlArray().then(imageFilenames => {
      const imageBaseUrl = "SISDP/Atlas/"; // Base URL for the images
      const imageUrls = imageFilenames.map(filename => `${imageBaseUrl}${filename}`);
     
      const swiperContainer2 = document.querySelector(".swiper2");
      const swiperWrapper2 = document.querySelector(".swiper-wrapper2");

      // Loop through the array and create an image element for each URL
      for (let i = 0; i < imageUrls.length; i++) {
        const imageUrl = imageUrls[i];
        const img = document.createElement("img");
        img.src = imageUrl;
        img.className = "swiper-slide"; // Set class to swiper-slide
        swiperWrapper2.appendChild(img);
      }

     

      // Swiper initialization function
      function initializeSwiper2() {
        var swiper2 = new Swiper('.swiper2', {
          slidesPerView: 1,
          loop: true,
          pagination: {
            el: '.swiper-pagination2',
            clickable: true,
          },
          autoplay: {
            delay: 5000, // Change slide every 5 seconds
            pauseOnMouseEnter: true,
            disableOnInteraction: false,
          },
           navigation: {
            nextEl: ".custom-next-button",
            prevEl: ".custom-prev-button",
          }, 
          spaceBetween: 0,
        });
      }

      initializeSwiper2();
    });
  });