importScripts('https://www.gstatic.com/firebasejs/10.13.2/firebase-app-compat.js');
importScripts('https://www.gstatic.com/firebasejs/10.13.2/firebase-messaging-compat.js');

firebase.initializeApp({
  apiKey: "AIzaSyBQX_NpjKiXrxVOuAvjs_w_MvwixQ_dP9w",
  authDomain: "jam-97f48.firebaseapp.com",
  projectId: "jam-97f48",
  storageBucket: "jam-97f48.firebasestorage.app",
  messagingSenderId: "1083343441316",
  appId: "1:1083343441316:web:59a18d1ab0cc487099c531"
});

const messaging = firebase.messaging();

messaging.onBackgroundMessage(function(payload) {
  console.log('[firebase-messaging-sw.js] Background message ', payload);
  const notificationTitle = payload.notification.title;
  const notificationOptions = {
    body: payload.notification.body,
    icon: '/icono-192.png'
  };
  self.registration.showNotification(notificationTitle, notificationOptions);
});
