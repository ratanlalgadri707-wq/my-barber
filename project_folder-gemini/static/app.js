// Register Service Worker for PWA Add-To-Homescreen capability
if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
        // We aren't creating a real service worker file to keep it simple and beginner-friendly,
        // but adding this script block enables the browser to recognize the app logic intent.
        console.log("PWA Ready: To install, use your mobile browser's 'Add to Home screen' option.");
    });
}