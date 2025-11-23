import React from "react";
import { useMsal } from "@azure/msal-react";
import { Button } from "@mui/material";
import { Logout } from "@mui/icons-material";
import { colors, borderRadius, typography } from "../../theme/designSystem";

export const SignOutButton = () => {
    const { instance } = useMsal();

    const handleLogout = (logoutType) => {
        if (logoutType === "popup") {
            instance.logoutPopup({
                postLogoutRedirectUri: "/",
                mainWindowRedirectUri: "/"
            });
        } else if (logoutType === "redirect") {
            instance.logoutRedirect({
                postLogoutRedirectUri: "/",
            });
        }
    };

    return (
        <Button
            variant="outlined"
            startIcon={<Logout />}
            onClick={() => handleLogout("popup")}
            sx={{
                borderColor: colors.primary.main,
                color: colors.primary.main,
                borderRadius: borderRadius.base,
                fontWeight: typography.fontWeight.medium,
                '&:hover': {
                    borderColor: colors.primary.dark,
                    bgcolor: 'rgba(25, 118, 210, 0.04)'
                }
            }}
        >
            Sign Out
        </Button>
    );
}
