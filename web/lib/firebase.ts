import { initializeApp, getApps, getApp, type FirebaseApp } from 'firebase/app';
import { getAuth, type Auth } from 'firebase/auth';

const firebaseConfig = {
  apiKey: process.env.NEXT_PUBLIC_FIREBASE_API_KEY,
  authDomain: process.env.NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN,
  projectId: process.env.NEXT_PUBLIC_FIREBASE_PROJECT_ID,
  storageBucket: process.env.NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET,
  messagingSenderId: process.env.NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID,
  appId: process.env.NEXT_PUBLIC_FIREBASE_APP_ID,
};

let app: FirebaseApp | undefined;
let auth: Auth | undefined;

function getFirebaseAuth(): Auth {
  if (!firebaseConfig.apiKey) {
    throw new Error('Firebase API key is not configured. Set NEXT_PUBLIC_FIREBASE_API_KEY in .env.local');
  }
  if (!app) {
    app = getApps().length === 0 ? initializeApp(firebaseConfig) : getApp();
  }
  if (!auth) {
    auth = getAuth(app);
  }
  return auth;
}

function isFirebaseConfigured(): boolean {
  return !!firebaseConfig.apiKey;
}

export { getFirebaseAuth, isFirebaseConfigured };
