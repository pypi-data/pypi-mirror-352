// noinspection ES6UnusedImports
import './globals';
import "./index.css";

function updateMaterialUITheme() {
    const body = document.body;
    const html = document.documentElement;

    // Check the current theme setting in JupyterLab
    const isLightTheme = body.getAttribute('data-jp-theme-light');

    // Update Material UI's theme attribute accordingly
    if (isLightTheme === "true" || isLightTheme === "false") {
        html.setAttribute('data-theme', isLightTheme ? 'light' : 'dark');
    }
}

// Create a new MutationObserver instance to listen for changes in the body tag's attributes
const observer = new MutationObserver(mutations => {
    mutations.forEach(mutation => {
        if (mutation.type === 'attributes' && mutation.attributeName === 'data-jp-theme-light') {
            updateMaterialUITheme();
        }
    });
});

const plugin = {
    id: "pret-joy:plugin", // app
    activate: () => null,
    autoStart: true,
};

// Start observing the body tag for attribute changes
observer.observe(document.body, {attributes: true});

// Initialize the theme when the script loads
updateMaterialUITheme();

export default plugin;
