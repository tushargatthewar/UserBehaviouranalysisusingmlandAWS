const MapBaseUrl = "SISDP/MapSlider/";
const MapBaseUrl2 = "SISDP/MapSlider/HighRes/";
const MapUrl = fetch("SISDP/CSV/Maps.csv")
  .then((response) => response.text())
  .then((csvData) => {
    const lines = csvData.split(',');
    const MapUrls = lines.map((line) => {
      const imageName = line.trim(); // Extract and trim the image name from the CSV line
      return {
        lowResUrl: MapBaseUrl + imageName + ".jpg", // Low-resolution image URL
        highResUrl: MapBaseUrl2 + imageName + ".jpg", // High-resolution image URL
      };
    });
    return MapUrls;
  });

const MapUrlArray = async () => {
  const images = await MapUrl;
  return images;
};

MapUrlArray().then(MapImages => {
  const MapSlider = document.querySelector(".map-container");

  // Loop through the array and create an image element for each URL
  for (let i = 0; i < MapImages.length; i++) {
    const { lowResUrl, highResUrl } = MapImages[i];
    
    // Create a container for each image to handle both low and high resolution
    const container = document.createElement("div");
    container.className = "MapSlideContainer";
    
    const lowResImg = document.createElement("img");
    lowResImg.src = lowResUrl;
    lowResImg.className = "LowResSlides";
    lowResImg.setAttribute("title", "Click for enlarged view"); // Tooltip text
    container.appendChild(lowResImg);

    const highResImg = document.createElement("img");
    highResImg.src = highResUrl;
    highResImg.className = "HighResSlides";
    highResImg.style.display = "none"; // Initially hide high-resolution image
    container.appendChild(highResImg);

    container.addEventListener("click", () => openHighResImage(highResUrl));

    MapSlider.appendChild(container);
  }

  var myIndex = 0;
  carousel();

  function carousel() {
    var i;
    var x = document.querySelectorAll(".MapSlideContainer");
    for (i = 0; i < x.length; i++) {
      x[i].style.display = "none";
    }
    myIndex++;
    if (myIndex > x.length) {
      myIndex = 1;
    }
    x[myIndex - 1].style.display = "flex";
    setTimeout(carousel, 3000); // Change image every 3 seconds
  }

  // Function to open a high-resolution image in a new page
  function openHighResImage(highResUrl) {
    window.open(highResUrl, '_blank');
  }
});
