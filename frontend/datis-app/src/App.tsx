import { Route, Switch } from "wouter";
import { Layout } from "@/components/layout";
import Dashboard from "@/pages/dashboard";
import DeepAnalysis from "@/pages/deep-analysis";
import Simulator from "@/pages/simulator";
import Portfolio from "@/pages/portfolio";
import Blockchain from "@/pages/blockchain";
import SocialNews from "@/pages/social-news";
import Failures from "@/pages/failures";
import NotFound from "@/pages/not-found";

export default function App() {
  return (
    <Layout>
      {({ selectedSymbol }) => (
        <Switch>
          <Route path="/">
            <Dashboard selectedSymbol={selectedSymbol} />
          </Route>
          <Route path="/analysis/:symbol">
            <DeepAnalysis />
          </Route>
          <Route path="/simulator">
            <Simulator />
          </Route>
          <Route path="/portfolio">
            <Portfolio />
          </Route>
          <Route path="/blockchain">
            <Blockchain />
          </Route>
          <Route path="/social-news">
            <SocialNews />
          </Route>
          <Route path="/failures">
            <Failures />
          </Route>
          <Route>
            <NotFound />
          </Route>
        </Switch>
      )}
    </Layout>
  );
}
