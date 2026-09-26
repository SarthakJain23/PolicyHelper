"use client";

import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Input } from "@/components/ui/input";
import { ChatSession } from "@/lib/api/types";
import { cn } from "@/lib/utils";
import {
  Check,
  Edit2,
  MessageSquare,
  MoreHorizontal,
  Pin,
  Trash2,
  X,
} from "lucide-react";
import React, { useState } from "react";

interface SessionItemProps {
  session: ChatSession;
  isActive: boolean;
  onSelect: (id: string) => void;
  onUpdate: (
    id: string,
    payload: { title?: string; is_pinned?: boolean; is_archived?: boolean },
  ) => void;
  onDelete: (id: string) => void;
}

export default function SessionItem({
  session,
  isActive,
  onSelect,
  onUpdate,
  onDelete,
}: SessionItemProps) {
  const [isEditing, setIsEditing] = useState(false);
  const [editedTitle, setEditedTitle] = useState(session.title);

  const handleSaveTitle = (e: React.MouseEvent | React.FormEvent) => {
    e.stopPropagation();
    if (editedTitle.trim() && editedTitle !== session.title) {
      onUpdate(session.id, { title: editedTitle.trim() });
    }
    setIsEditing(false);
  };

  const handleCancelEdit = (e: React.MouseEvent) => {
    e.stopPropagation();
    setEditedTitle(session.title);
    setIsEditing(false);
  };

  return (
    <div
      onClick={() => onSelect(session.id)}
      className={cn(
        "group relative flex items-center justify-between rounded-lg px-2.5 py-2 text-xs transition-colors cursor-pointer select-none",
        isActive
          ? "bg-neutral-200/70 font-semibold text-neutral-900 dark:bg-neutral-800 dark:text-neutral-50"
          : "text-neutral-700 hover:bg-neutral-100 hover:text-neutral-900 dark:text-neutral-400 dark:hover:bg-neutral-900 dark:hover:text-neutral-100",
      )}
    >
      <div className="flex items-center space-x-2 truncate pr-2">
        <MessageSquare
          className={cn(
            "h-3.5 w-3.5 shrink-0",
            isActive
              ? "text-neutral-900 dark:text-neutral-50"
              : "text-neutral-400",
          )}
        />

        {isEditing ? (
          <form
            onSubmit={handleSaveTitle}
            onClick={(e) => e.stopPropagation()}
            className="flex items-center space-x-1"
          >
            <Input
              value={editedTitle}
              onChange={(e) => setEditedTitle(e.target.value)}
              className="h-6 w-36 px-1.5 text-xs py-0"
              autoFocus
            />
            <Button
              size="icon"
              variant="ghost"
              type="submit"
              className="h-6 w-6"
            >
              <Check className="h-3 w-3 text-emerald-600" />
            </Button>
            <Button
              size="icon"
              variant="ghost"
              type="button"
              onClick={handleCancelEdit}
              className="h-6 w-6"
            >
              <X className="h-3 w-3 text-red-500" />
            </Button>
          </form>
        ) : (
          <span className="truncate">{session.title}</span>
        )}
      </div>

      {!isEditing && (
        <div className="flex items-center space-x-1 shrink-0 opacity-0 group-hover:opacity-100 transition-opacity">
          {session.is_pinned && (
            <Pin className="h-3 w-3 text-neutral-400 fill-neutral-400" />
          )}

          <DropdownMenu>
            <DropdownMenuTrigger asChild onClick={(e) => e.stopPropagation()}>
              <Button
                variant="ghost"
                size="icon"
                className="h-6 w-6 text-neutral-400 hover:text-neutral-800"
              >
                <MoreHorizontal className="h-3 w-3" />
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end" className="w-36">
              <DropdownMenuItem
                onClick={(e) => {
                  e.stopPropagation();
                  setIsEditing(true);
                }}
                className="text-xs"
              >
                <Edit2 className="mr-2 h-3 w-3" />
                <span>Rename</span>
              </DropdownMenuItem>
              <DropdownMenuItem
                onClick={(e) => {
                  e.stopPropagation();
                  onUpdate(session.id, { is_pinned: !session.is_pinned });
                }}
                className="text-xs"
              >
                <Pin className="mr-2 h-3 w-3" />
                <span>{session.is_pinned ? "Unpin" : "Pin Session"}</span>
              </DropdownMenuItem>
              <DropdownMenuItem
                onClick={(e) => {
                  e.stopPropagation();
                  onDelete(session.id);
                }}
                className="text-xs text-red-600 focus:text-red-600"
              >
                <Trash2 className="mr-2 h-3 w-3" />
                <span>Delete</span>
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
      )}
    </div>
  );
}
