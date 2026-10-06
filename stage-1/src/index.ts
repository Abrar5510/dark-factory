import express from 'express';
import cors from 'cors';
import { Database } from './database';
import { errorHandler } from './middleware/errorHandler';
import { authRoutes } from './routes/auth';
import { userRoutes } from './routes/user';
import { paymentRoutes } from './routes/payments';
import { requestRoutes } from './routes/requests';
import { splitRoutes } from './routes/splits';
import { settlementRoutes } from './routes/settlements';
import { activityRoutes } from './routes/activity';
import { testRoutes } from './routes/test';

const app = express();
const port = process.env.PORT || '8080';

// Initialize database
const db = Database.getInstance();

// Middleware
app.use(cors());
app.use(express.json({ limit: '10mb' }));
app.use(express.urlencoded({ extended: true }));

// Health endpoint
app.get('/health', (req, res) => {
  res.status(200).json({ status: 'ok' });
});

// Routes
app.use('/auth', authRoutes);
app.use(userRoutes); // /me
app.use('/payments', paymentRoutes);
app.use('/requests', requestRoutes);
app.use('/splits', splitRoutes);
app.use('/settlements', settlementRoutes);
app.use('/activity', activityRoutes);
app.use('/_test', testRoutes);

// Error handling
app.use(errorHandler);

// Start server
const server = app.listen(parseInt(port), '0.0.0.0', () => {
  console.log(`Pocketful service listening on port ${port}`);
});

// Graceful shutdown
process.on('SIGTERM', () => {
  console.log('SIGTERM received, shutting down gracefully');
  server.close(() => {
    db.close();
    console.log('Server closed');
    process.exit(0);
  });
});

process.on('SIGINT', () => {
  console.log('SIGINT received, shutting down gracefully');
  server.close(() => {
    db.close();
    console.log('Server closed');
    process.exit(0);
  });
});

export default app;