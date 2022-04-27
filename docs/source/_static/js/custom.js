const videos = document.querySelectorAll("video");
for(let video of videos) {
  video.pause();
}

const h2Grp = document.querySelectorAll("h2")
for(let _h2 of h2Grp) {
    _h2.style.color = "red"
}