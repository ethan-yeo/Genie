import ChatIcon from "@mui/icons-material/Chat";
import InsertDriveFileIcon from '@mui/icons-material/InsertDriveFile';
import "./MainNavBar.css";

export const MainNavBarData = [
  {
    icon: <ChatIcon className="svg-icon" />,
    title: "RAG",
    link: "",
  },
  {
    icon: <InsertDriveFileIcon className="svg-icon" />,
    title: "Batch File Query",
    link: "batchfilequery",
  },
];
