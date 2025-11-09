# AI Knowledge Engine

A modern React frontend application for analyzing customer support tickets using AI-powered insights and recommendations.

## Features

- **Ticket Analysis**: Upload or paste support tickets for AI-powered analysis
- **Smart Recommendations**: Get instant suggestions for relevant articles and solutions
- **Analytics Dashboard**: View metrics and insights with interactive charts
- **Responsive Design**: Clean, modern UI built with Tailwind CSS
- **Mock API Integration**: Ready to connect to FastAPI backend

## Tech Stack

- **React 18** - Frontend framework
- **Vite** - Build tool and development server
- **Tailwind CSS** - Utility-first CSS framework
- **React Router** - Client-side routing
- **Axios** - HTTP client for API calls
- **Recharts** - Chart library for analytics
- **Lucide React** - Beautiful icon library

## Getting Started

### Prerequisites

- Node.js (version 16 or higher)
- npm or yarn

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd ai-knowledge-engine
```

2. Install dependencies:
```bash
npm install
```

3. Start the development server:
```bash
npm run dev
```

4. Open your browser and navigate to `http://localhost:5173`

### Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run lint` - Run ESLint

## Project Structure

```
src/
├── components/          # Reusable UI components
│   ├── Navbar.jsx      # Navigation component
│   ├── TicketUpload.jsx # Ticket upload and analysis
│   ├── RecommendationPanel.jsx # Analysis results display
│   └── Dashboard.jsx   # Analytics dashboard
├── pages/              # Page components
│   ├── Home.jsx        # Landing page
│   ├── Analytics.jsx   # Analytics page
│   └── NotFound.jsx    # 404 page
├── api/                # API configuration
│   └── axiosConfig.js  # Axios setup
├── App.jsx             # Main app component with routing
├── main.jsx            # Application entry point
└── index.css           # Global styles and Tailwind imports
```

## API Integration

The app is configured to work with a FastAPI backend. The API configuration is set up in `src/api/axiosConfig.js` with the following endpoints:

- `POST /analyze_ticket` - Analyze support ticket content

### Environment Variables

Create a `.env` file in the root directory:

```env
VITE_API_URL=http://localhost:8000
```

## Features Overview

### Home Page
- Hero section with app introduction
- Feature highlights
- Ticket upload component with analysis functionality

### Analytics Page
- Interactive dashboard with charts
- Ticket volume and resolution metrics
- Category distribution
- Response time trends
- Recent activity feed

### Ticket Analysis
- Text area for ticket input
- AI-powered analysis with category detection
- Sentiment analysis
- Priority assessment
- Recommended articles
- Key topic extraction

## Styling

The app uses Tailwind CSS with custom components and utilities:

- Custom color palette with primary blues
- Responsive design for all screen sizes
- Consistent spacing and typography
- Modern card-based layouts
- Interactive hover states and transitions

## Development

### Adding New Features

1. Create components in the `src/components/` directory
2. Add new pages in the `src/pages/` directory
3. Update routing in `src/App.jsx` as needed
4. Follow the existing code structure and naming conventions

### API Integration

When connecting to the FastAPI backend:

1. Update the base URL in `src/api/axiosConfig.js`
2. Modify the mock data in `TicketUpload.jsx` to use real API responses
3. Add proper error handling for API failures
4. Implement loading states and user feedback

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is licensed under the MIT License.
