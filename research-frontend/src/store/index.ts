import { configureStore } from '@reduxjs/toolkit';
import appReducer from './slices/appSlice';
import chatReducer from './slices/chatSlice';
import notebookReducer from './slices/notebookSlice';

export const store = configureStore({
  reducer: {
    app: appReducer,
    chat: chatReducer,
    notebook: notebookReducer,
  },
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware({
      serializableCheck: {
        ignoredActions: ['persist/PERSIST'],
      },
    }),
});

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;
