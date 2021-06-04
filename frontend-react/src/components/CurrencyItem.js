const CurrencyItem = ({ index, data: { name, rate, fee, real_rate, url, note, modified } }) => {
  return (
    <tr className="border-b border-gray-700">
      <td>{index + 1}</td>
      <td className="py-1">
        <a
          className="px-1 text-blue-400 hover:underline"
          href={url}
          target="_blank"
          rel="noopener noreferrer"
        >
          {name}
        </a>
      </td>
      <td className="">
        <div className="inline-flex text-green-400 rounded-md px-2">{real_rate}</div>
      </td>
      <td>
        {rate !== real_rate ? (
          <div className="px-1 text-gray-400">{rate}</div>
        ) : (
          <div className="text-center">-</div>
        )}
      </td>
      <td>
        {rate !== real_rate ? (
          <div className="inline-flex text-pink-400 rounded-md px-1">{fee}</div>
        ) : (
          <div className="text-center">-</div>
        )}
      </td>
      <td className="hidden sm:block">
        {note ? <div className="inline-flex text-yellow-400 px-1 break-all">{note}</div> : ""}
      </td>
    </tr>
  );
};

export default CurrencyItem;
