import { useState, useEffect } from "react";
import { formatDistance } from "date-fns";
import CurrencyItem from "./CurrencyItem";

const CurrencyList = () => {
  const [currencies, setCurrencies] = useState([]);
  const [lastUpdate, setLastUpdate] = useState("");

  const getData = async () => {
    const res = await fetch("http://localhost:8000/data");
    const data = await res.json();
    // console.log(data);
    setCurrencies(data);

    if (data && data.length > 0) {
      const dataSortedByModified = [...data].sort((a, b) => {
        if (new Date(a.modified) > new Date(b.modified)) return -1;
        if (new Date(a.modified) < new Date(b.modified)) return 1;
      });

      const lastUpdate = dataSortedByModified[0].modified;
      if (lastUpdate) {
        setLastUpdate(formatDistance(new Date(lastUpdate), new Date()) + " ago");
      }
    }
  };

  useEffect(() => {
    getData();
    setInterval(getData, 60 * 1000);
  }, []);

  return (
    <div className="flex flex-col items-center justify-between">
      {currencies && currencies.length === 0 ? (
        <div className="text-center">Loading...</div>
      ) : (
        <table className="table-auto">
          <thead>
            <tr className="border-b-2 border-gray-700">
              <th className="font-medium">No</th>
              <th className="font-medium">Name</th>
              <th className="font-medium">Real rate</th>
              <th className="font-medium">Rate</th>
              <th className="font-medium">Fee</th>
              <th className="hidden sm:block font-medium">Note</th>
            </tr>
          </thead>
          <tbody>
            {currencies.map((currency, index) => {
              return <CurrencyItem key="currency.name" index={index} data={currency} />;
            })}
          </tbody>
        </table>
      )}

      <div className="mt-3">{lastUpdate}</div>
    </div>
  );
};

export default CurrencyList;
