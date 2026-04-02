let lastLeafTime = 0;

document.addEventListener('mousemove', function(e) {
    let currentTime = new Date().getTime();
    
    // Har 50 milliseconds mein ek leaf banegi (Performance ke liye)
    if (currentTime - lastLeafTime < 50) return;
    lastLeafTime = currentTime;

    // Naya leaf element banana
    let leaf = document.createElement('i');
    leaf.className = 'fa-solid fa-leaf falling-leaf'; // FontAwesome class
    
    // Leaf ko wahan set karna jahan mouse hai
    leaf.style.left = e.clientX + 'px';
    leaf.style.top = e.clientY + 'px';
    
    // Random size
    let size = Math.random() * 15 + 10; 
    leaf.style.fontSize = size + 'px';
    
    // Random animation speed (1.5 seconds se 3.5 seconds)
    let duration = Math.random() * 2 + 1.5; 
    leaf.style.animationDuration = duration + 's';
    
    // Screen par add karna
    document.body.appendChild(leaf);
    
    // Animation poora hone ke baad leaf ko delete karna taaki lag na ho
    setTimeout(() => {
        if (leaf && leaf.parentNode) {
            leaf.parentNode.removeChild(leaf);
        }
    }, duration * 1000);
});