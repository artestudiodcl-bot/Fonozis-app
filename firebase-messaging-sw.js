// Importa librerías de Firebase
importScripts('https://www.gstatic.com/firebasejs/10.13.2/firebase-app-compat.js');
importScripts('https://www.gstatic.com/firebasejs/10.13.2/firebase-messaging-compat.js');

// Inicializa Firebase en el service worker
firebase.initializeApp({
  apiKey: "AIzaSyBQX_NpjKiXrxVOuAvjs_w_MvwixQ_dP9w",
  authDomain: "jam-97f48.firebaseapp.com",
  projectId: "jam-97f48",
  storageBucket: "jam-97f48.firebasestorage.app",
  messagingSenderId: "1083343441316",
  appId: "1:1083343441316:web:59a18d1ab0cc487099c531"
});

// Obtén la instancia de Messaging
const messaging = firebase.messaging();
