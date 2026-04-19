import { Route, Routes } from 'react-router-dom';

import AppLayout from './layouts/AppLayout';
import DashboardPage from './pages/DashboardPage';
import NewsFeedPage from './pages/NewsFeedPage';
import SignalsPage from './pages/SignalsPage';
import TickerViewPage from './pages/TickerViewPage';

function App() {
  return (
    <Routes>
      <Route path="/" element={<AppLayout />}>
        <Route index element={<DashboardPage />} />
        <Route path="ticker" element={<TickerViewPage />} />
        <Route path="news" element={<NewsFeedPage />} />
        <Route path="signals" element={<SignalsPage />} />
      </Route>
    </Routes>
  );
}

export default App;
