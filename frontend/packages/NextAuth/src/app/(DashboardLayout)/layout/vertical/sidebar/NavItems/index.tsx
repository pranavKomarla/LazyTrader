"use client";
import React from "react";
import { ChildItem } from "../Sidebaritems";
import { Sidebar, SidebarItem} from "flowbite-react";
import { Icon } from "@iconify/react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { useTranslation } from 'react-i18next';

interface NavItemsProps {
  item: ChildItem;
}
const NavItems: React.FC<NavItemsProps> = ({ item }) => {
  const pathname = usePathname();
  const { t } = useTranslation();
  return (
    <>
      <SidebarItem
        href={item.url}
        as={Link}
        className={`${item.url == pathname
          ? "!text-primary bg-lightprimary "
          : "text-link bg-transparent group/link "
          } `}
      >
        <span className="flex gap-3 align-center items-center truncate text-[15px]">
          {item.icon ? (
            <Icon icon={item.icon} className={`${item.color}`} height={18} />
          ) : (
            <span
              className={`${item.url == pathname
                ? "dark:bg-white rounded-full mx-1.5 group-hover/link:bg-primary !bg-primary h-[6px] w-[6px]"
                : "h-[6px] w-[6px] bg-darklink dark:bg-white rounded-full mx-1.5 group-hover/link:bg-primary"
                } `}
            ></span>
          )}
          {t(`${item.name}`)}
        </span>
      </SidebarItem>
    </>
  );
};

export default NavItems;
