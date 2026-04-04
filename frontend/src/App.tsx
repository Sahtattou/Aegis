import { MainLayout } from "./components/layout/MainLayout";

function App() {
  return (
    <MainLayout>
      <section className="rounded-lg border border-dashed border-slate-300 bg-white p-10">
        <h1 className="text-2xl font-semibold">Dashboard</h1>
        <p className="mt-2 text-sm text-slate-600">
          Empty dashboard area ready for widgets and content.
        </p>
      </section>
    </MainLayout>
  );
}

export default App;
