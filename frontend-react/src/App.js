import { BrowserRouter as Router, Switch, Route } from "react-router-dom";
import Navbar from "./components/Navbar";
import Footer from "./components/Footer";
import CurrencyList from "./components/CurrencyList";

function App() {
  return (
    <div className="text-gray-300">
      <Router>
        <Navbar />
        <Switch>
          <Route exact path="/">
            <CurrencyList />
          </Route>
        </Switch>
        <Footer />
      </Router>
    </div>
  );
}

export default App;
