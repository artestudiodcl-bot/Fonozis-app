// Importa Firebase
importScripts('https://www.gstatic.com/firebasejs/10.13.2/firebase-app-compat.js');
importScripts('https://www.gstatic.com/firebasejs/10.13.2/firebase-messaging-compat.js');

// Configuración de tu proyecto
firebase.initializeApp({
  apiKey: "AIzaSyBQX_NpjKiXrxVOuAvjs_w_MvwixQ_dP9w",
  authDomain: "jam-97f48.firebaseapp.com",
  projectId: "jam-97f48",
  storageBucket: "jam-97f48.firebasestorage.app",
  messagingSenderId: "1083343441316",
  appId: "1:1083343441316:web:59a18d1ab0cc487099c531"
});

// Instancia de Messaging
const messaging = firebase.messaging();

// Notificación en primer plano
messaging.onBackgroundMessage(function(payload) {
  console.log('[firebase-messaging-sw.js] Received background message ', payload);
  const notificationTitle = payload.notification.title;
  const notificationOptions = {
    body: payload.notification.body,
    icon: '/icono-192.png'
  };

  self.registration.showNotification(notificationTitle, notificationOptions);
});
