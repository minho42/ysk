import { Link } from "react-router-dom";

const Navbar = () => {
  return (
    <nav>
      <header className="flex justify-center border-b border-gray-500 shadow-sm">
        <div className="flex items-center justify-between pl-3 py-2 h-12">
          <div className="flex items-center">
            <Link to="/" className="px-1 py-1 font-semibold text-lg text-gray-200 hover:text-gray-300">
              호주 역송금 비교
            </Link>
          </div>
        </div>
      </header>
    </nav>
  );
};

export default Navbar;
