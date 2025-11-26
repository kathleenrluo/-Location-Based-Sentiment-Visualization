# Sentiment Visualization - Location-Based Emotion Tracking

An interactive web application for visualizing location-based sentiment data over time. Built with Vue.js, deck.gl, and Bootstrap.

## Features

- **Daily Mode**: View sentiment data for a single day with a 24-hour timeline slider
- **Lifetime Mode**: Aggregate sentiment patterns across multiple days, grouped by time-of-day
- **Interactive Map**: Explore sentiment data on an interactive map with building footprints
- **Sentiment Visualization**: Color-coded dots representing emotional states (green = positive, red = negative, yellow = neutral)
- **Striped Dots**: Visual representation of multiple intervals at the same location
- **Building Footprints**: Complete building polygon data for USC area

## Prerequisites

- Node.js (v20.9.0 or higher)
- npm (v10.1.0 or higher)

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd project-team12
```

2. Install dependencies:
```bash
npm install
```

## Running the Application

### Development Mode

Start the development server:
```bash
npm run dev
```

The application will be available at `http://localhost:5173` (or the port shown in the terminal).

### Production Build

Build for production:
```bash
npm run build
```

Preview the production build:
```bash
npm run preview
```

## How to Use

### View Modes

**Daily View** (Default):
- Shows sentiment data for individual time intervals
- Use the 24-hour timeline slider to filter intervals by time of day
- Each dot represents a single location visit
- Dot size indicates duration of stay
- Dot color indicates sentiment (green = positive, red = negative, yellow = neutral)

**Lifetime View**:
- Aggregates sentiment data across all days
- Groups data by time-of-day buckets (3-hour windows)
- Shows long-term patterns and routines
- Useful for identifying consistent emotional patterns at specific locations

### Controls

1. **View Mode Toggle**: Switch between Daily and Lifetime views using the buttons in the top-right control panel

2. **Map Interaction**:
   - **Pan**: Click and drag to move around the map
   - **Zoom**: Use mouse wheel or pinch gesture
   - **Hover**: Hover over sentiment dots to see details (tooltip coming soon)

### Understanding the Visualization

- **Green Dots**: Positive sentiment (sentiment score > 0.3)
- **Red Dots**: Negative sentiment (sentiment score < -0.3)
- **Yellow Dots**: Neutral sentiment (between -0.3 and 0.3)
- **Fixed Size**: All dots are 8px radius, showing aggregate sentiment per location
- **Colored Buildings**: Buildings are colored by sentiment of nearby intervals
- **Gray Lines**: Travel paths between consecutive location visits

### Data Structure

The application uses three main data files (served from `public/`):

1. **intervals.json**: Time-stamped location visits with sentiment scores
2. **locations.json**: Key location coordinates (home, library, gym, etc.)
3. **buildings_usc.geojson**: Building footprint polygons for the USC area

Source data and processing scripts are in the `data/` directory. See `data/README.md` for details.

## Project Structure

```
project-team12/
├── src/
│   ├── components/
│   │   └── MapVisualization.vue  # Main map component
│   ├── utils/
│   │   └── dataLoader.js          # Data loading and processing utilities
│   ├── App.vue                    # Root component
│   └── main.js                    # Application entry point
├── public/
│   ├── intervals.json             # Time interval data (served to web app)
│   ├── locations.json             # Location coordinates (served to web app)
│   └── buildings_usc.geojson     # Building footprints (served to web app)
├── data/
│   ├── intervals.json             # Source interval data
│   ├── locations.json             # Source location data
│   ├── buildings_usc.geojson      # Source building data
│   ├── process_data.py            # Data generation script
│   └── README.md                  # Data directory documentation
├── docs/
│   ├── development.md             # Development log
│   ├── DATA_REQUIREMENTS.md       # Data requirements guide
│   ├── designdoc.txt              # Design specifications
│   └── README.md                  # Documentation index
├── package.json
├── vite.config.js
└── index.html
```

## Technologies Used

- **Vue.js 3**: Progressive JavaScript framework
- **deck.gl**: WebGL-powered visualization framework
- **Mapbox GL JS**: Interactive map rendering
- **Bootstrap 5**: Responsive UI components
- **Vite**: Build tool and development server

## Development

### Adding New Features

1. Data processing utilities are in `src/utils/dataLoader.js`
2. Map visualization logic is in `src/components/MapVisualization.vue`
3. See `docs/development.md` for detailed development log

### Regenerating Data

To regenerate synthetic data:
```bash
cd data
python process_data.py
# Then copy output files to public/
cp intervals.json locations.json buildings_usc.geojson ../public/
```

### Data Format

Intervals data structure:
```json
{
  "start_time": "2024-11-18T07:00:00",
  "end_time": "2024-11-18T08:30:00",
  "location_name": "Home",
  "location_type": "home",
  "latitude": 34.025,
  "longitude": -118.29,
  "sentiment_score": 0.08,
  "activity": "morning_routine",
  "duration_minutes": 90
}
```

## Deployment

For GitHub Pages deployment:

1. Build the project:
```bash
npm run build
```

2. Configure `vite.config.js` with the correct `base` path for your repository

3. Deploy the `dist` folder to GitHub Pages

See the [Vue example](https://github.com/dsci-554/vue-example) for detailed deployment instructions.

## Troubleshooting

**Map not loading?**
- Check that Mapbox access token is valid (currently using public demo token)
- Ensure data files are in the `public/` directory

**No data showing?**
- Verify that `intervals.json`, `locations.json`, and `buildings_usc.geojson` are in the `public/` folder
- Check browser console for errors

**Build errors?**
- Ensure all dependencies are installed: `npm install`
- Check Node.js version compatibility

## License

This project is part of DSCI 554 coursework at USC.

## Contributors

Team 12 - DSCI 554
